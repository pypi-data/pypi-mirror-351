'''Tests for image_dir.py.'''

import math
from pathlib import Path

# pylint: disable=no-name-in-module,duplicate-code
import tensorflow as tf  # type: ignore[import]

from ngautonml.config_components.dataset_config import DatasetConfig

from .image_tensor_data_loader import ImageTensorDataLoader


NUM_IMAGES = 3665

MINIMAL_CLAUSE = {
    'config': 'image_dir',
    'params': {
        'train_dir': str(Path(__file__).parents[4] / 'examples' / 'flowers' / 'train')
    }
}


def test_defaults() -> None:
    '''Test that default parameters get applied when not specified.'''
    config = DatasetConfig(MINIMAL_CLAUSE)
    dut = ImageTensorDataLoader(config)
    dataset = dut.load_train()
    assert dataset is not None
    got = dataset['keras_ds']
    assert isinstance(got, tf.data.Dataset)
    assert got.class_names == ['daisy', 'dandelion', 'roses', 'sunflowers', 'tulips']
    for image_batch, _ in got:
        # shape tuple is (batch_size, img_height, img_width, _)
        assert image_batch.shape == (32, 128, 128, 3)
        break
    want_val_split = 1 - 0.2
    num_images_got = len([1 for _ in got.unbatch()])
    num_images_want = math.floor(NUM_IMAGES * want_val_split)
    assert num_images_got == num_images_want


OVERRIDE_CLAUSE = {
    'config': 'image_dir',
    'params': {
        'train_dir': str(Path(__file__).parents[4] / 'examples' / 'flowers' / 'train'),
        'validation_split': 0.6,
        'img_height': 2,
        'img_width': 8,
        'batch_size': 10
    }
}


def test_overrides() -> None:
    '''Test that overridden parameters get properly applied.'''
    config = DatasetConfig(OVERRIDE_CLAUSE)
    dut = ImageTensorDataLoader(config=config)
    dataset = dut.load_train()
    assert dataset is not None
    got = dataset['keras_ds']
    assert isinstance(got, tf.data.Dataset)
    for image_batch, _ in got:
        # shape tuple is (batch_size, img_height, img_width, _)
        assert image_batch.shape == (10, 2, 8, 3)
        break
    want_val_split = 1 - 0.6
    num_images_got = len([1 for _ in got.unbatch()])
    num_images_want = math.floor(NUM_IMAGES * want_val_split)
    assert num_images_got == num_images_want
