'''Tests for image_tensor_params.py.'''
# mypy: disable-error-code="attr-defined"

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from .image_tensor_params import ImageTensorParams

# pylint: disable=missing-function-docstring,duplicate-code


def test_basic_params() -> None:
    clause = {
        'train_dir': '/some/path'
    }

    dut = ImageTensorParams(clause=clause)

    assert dut.train_dir == '/some/path'


def test_defaullted_param() -> None:
    clause = {
        'train_dir': '/some/path'
    }

    dut = ImageTensorParams(clause=clause)

    assert dut.batch_size == 32


def test_chrismas_tree() -> None:
    clause = {
        'train_dir': '/some/train/path',
        'test_dir': '/some/test/path',
        'validation_split': 0.9,
        'seed': 1701,
        'img_height': 1024,
        'img_width': 1024,
        'batch_size': 10,
    }

    dut = ImageTensorParams(clause=clause)

    assert dut.train_dir == '/some/train/path'
    assert dut.test_dir == '/some/test/path'
    assert dut.validation_split == 0.9
    assert dut.seed == 1701
    assert dut.img_height == 1024
    assert dut.img_width == 1024
    assert dut.batch_size == 10
