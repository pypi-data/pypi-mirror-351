'''Tests for Sequential algorithm for TensorFlow Keras.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Tuple

import pandas as pd
import pytest
import tensorflow as tf
import keras  # type: ignore[import-untyped]

from ngautonml.metrics.impl.metric_auto import MetricCatalogAuto
from ngautonml.problem_def.task import TaskType, DataType
from ngautonml.tables.impl.table_auto import TableCatalogAuto
from ngautonml.wrangler.dataset import Column, Dataset, DatasetKeys, Metadata, RoleName

from .sequential import KerasSequential
# pylint: disable=missing-function-docstring, protected-access,duplicate-code
TableCatalogAuto()


def load_classification_dataset() -> Tuple[Dataset, Dataset, Dataset]:
    batch_size = 32
    img_height = 180
    img_width = 180

    train_dir = 'examples/flowers/train/'
    test_dir = 'examples/flowers/test'

    metadata = Metadata(
        roles={RoleName.TARGET: [Column('target')]},
        task=TaskType.MULTICLASS_CLASSIFICATION,
        data_type=DataType.IMAGE
    )

    train_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)
    assert isinstance(train_ds, tf.data.Dataset)

    val_ds = keras.utils.image_dataset_from_directory(
        train_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)
    assert isinstance(val_ds, tf.data.Dataset)

    test_ds = keras.utils.image_dataset_from_directory(
        test_dir,
        labels=None,
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size,
        shuffle=False)

    assert isinstance(test_ds, tf.data.Dataset)

    dataset = Dataset(
        metadata=metadata,
        keras_ds=train_ds,
        keras_validate=val_ds
    )

    test = Dataset(
        metadata=metadata,
        keras_ds=test_ds
    )

    truthiness = pd.DataFrame(['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips'],
                              columns=['target'])
    truth = Dataset(
        metadata=metadata,
        ground_truth=truthiness
    )
    return dataset, test, truth


def test_sunny_day() -> None:

    keras.utils.set_random_seed(123)
    tf.config.experimental.enable_op_determinism()
    metric_catalog = MetricCatalogAuto()

    trn_data, test_data, ground_truth = load_classification_dataset()

    class_names = trn_data[DatasetKeys.KERAS_DS.value].class_names

    num_classes = len(class_names)

    algorithm = KerasSequential(img_height=180, img_width=180, epochs=2, num_classes=num_classes)
    dut = algorithm.instantiate()

    dut.fit(trn_data)

    result = dut.predict(test_data)

    metric = metric_catalog.lookup_by_name('accuracy_score')
    assert metric.calculate(pred=result,
                            ground_truth=ground_truth
                            ) == pytest.approx(0.8, 0.26)
