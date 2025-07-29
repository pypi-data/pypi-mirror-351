'''Tests replicating example notebooks.'''
# pylint: disable=missing-function-docstring,missing-class-docstring

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from glob import glob
import os
from pathlib import Path
import subprocess

from ngautonml.algorithms.impl.algorithm_auto import FakeAlgorithmCatalogAuto
from ngautonml.problem_def.problem_def import ProblemDefinition
from ngautonml.tables.impl.table_auto import TableCatalogAuto
from ngautonml.wrangler.wrangler import Wrangler
# pylint: disable=duplicate-code
TableCatalogAuto()


def module_path() -> Path:
    return Path(__file__).parents[3]


def flowers_config():
    train_dir = module_path() / 'examples' / 'flowers' / 'train'
    test_dir = module_path() / 'examples' / 'flowers' / 'test'
    pdef = {
        "dataset": {
            "config": "image_tensor",
            "train_dir": train_dir,
            "test_dir": test_dir
        },
        "problem_type": {
            "data_type": "IMAGE",
            "task": "MULTICLASS_CLASSIFICATION"
        },
        "cross_validation": {
            "k": 1
        },
        "hyperparams": [
            {
                "_comments": [
                    "We need fewer epochs for a test environment without GPU."
                ],
                "select": {
                    "algorithm": "tf.keras.sequential"
                },
                "params": {
                    "epochs": {
                        "fixed": 2
                    }
                }
            }
        ]
    }
    return ProblemDefinition(pdef)


def test_wrangle_image() -> None:
    plugin_root = Path(__file__).parents[1]
    env = os.environ.copy()

    subprocess.run(['python', '-m', 'build'], cwd=plugin_root, check=True)

    pluginpaths = glob(str(plugin_root / 'dist' / 'ngautonml_image-*py3-none-any.whl'))
    assert len(pluginpaths) == 1, f'BUG: unexpected extra whl files: {pluginpaths}'
    pluginpath = Path(pluginpaths[0])
    subprocess.run(['pip', 'install', pluginpath], check=True, env=env)

    problem_definition = flowers_config()
    dut = Wrangler(
        problem_definition=problem_definition,
        algorithm_catalog=FakeAlgorithmCatalogAuto
    )
    got = dut.fit_predict_rank()

    assert list(got.train_results.values())[0].prediction.predictions_table.shape == (733, 1)

    subprocess.run(['pip', 'uninstall', '-y', pluginpath], check=False)
