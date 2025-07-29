'''Params parser for ImageTensorDataLoader.'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from enum import Enum
from typing import Set

from ngautonml.config_components.impl.config_component import ConfigComponent


class ImageTensorParams(ConfigComponent):
    '''Params parser for ImageTensorDataLoader'''

    class Keys(Enum):
        '''Child classes need to define this class with all their keys.'''
        TRAIN_DIR = 'train_dir'
        TEST_DIR = 'test_dir'
        VALIDATION_SPLIT = 'validation_split'
        SEED = 'seed'
        IMG_HEIGHT = 'img_height'
        IMG_WIDTH = 'img_width'
        BATCH_SIZE = 'batch_size'

    Defaults = {
        Keys.TRAIN_DIR: None,
        Keys.TEST_DIR: None,
        Keys.VALIDATION_SPLIT: 0.2,
        Keys.SEED: 123,
        Keys.IMG_HEIGHT: 128,
        Keys.IMG_WIDTH: 128,
        Keys.BATCH_SIZE: 32,
    }

    def required_keys(self) -> Set[str]:
        keys = super().required_keys()
        keys.update({
            self.Keys.TRAIN_DIR.value
        })
        return keys

    def validate(self, **kwargs) -> None:
        pass

    @property
    def train_dir(self):
        '''train_dir'''
        return self._get_with_default(self.Keys.TRAIN_DIR.value,
                                      dflt=self.Defaults[self.Keys.TRAIN_DIR])

    @property
    def test_dir(self):
        '''test_dir'''
        return self._get_with_default(self.Keys.TEST_DIR.value,
                                      dflt=self.Defaults[self.Keys.TEST_DIR])

    @property
    def validation_split(self):
        '''validation_split'''
        return self._get_with_default(self.Keys.VALIDATION_SPLIT.value,
                                      dflt=self.Defaults[self.Keys.VALIDATION_SPLIT])

    @property
    def seed(self):
        '''seed'''
        return self._get_with_default(self.Keys.SEED.value,
                                      dflt=self.Defaults[self.Keys.SEED])

    @property
    def img_height(self):
        '''img_height'''
        return self._get_with_default(self.Keys.IMG_HEIGHT.value,
                                      dflt=self.Defaults[self.Keys.IMG_HEIGHT])

    @property
    def img_width(self):
        '''img_width'''
        return self._get_with_default(self.Keys.IMG_WIDTH.value,
                                      dflt=self.Defaults[self.Keys.IMG_WIDTH])

    @property
    def batch_size(self):
        '''batch_size'''
        return self._get_with_default(self.Keys.BATCH_SIZE.value,
                                      dflt=self.Defaults[self.Keys.BATCH_SIZE])
