'''Datasetloader for image classification, using tensorflow format.

Images are stored in subdirectories whose names indicate thier class.
'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Any, Dict, List, Optional

import tensorflow as tf


from ngautonml.config_components.dataset_config import DatasetConfig
from ngautonml.config_components.impl.config_component import ValidationErrors
from ngautonml.data_loaders.impl.data_loader import DataLoader
from ngautonml.data_loaders.impl.data_loader_catalog import DataLoaderCatalog
from ngautonml.problem_def.output_config import ConfigError
from ngautonml.wrangler.constants import Defaults
from ngautonml.wrangler.dataset import Column, Dataset, Metadata, RoleName

from .impl.image_tensor_params import ImageTensorParams


class ImageTensorDataLoader(DataLoader):
    '''Holds information about an image classification dataset.

    Images are stored in subdirectories whose names indicate thier class.
    '''
    name = 'image_tensor'
    tags: Dict[str, List[str]] = {
        'input_format': ['image_directory'],
        'loaded_format': ['tensorflow_tensor']
    }
    _config: DatasetConfig
    _metadata: Metadata
    _params: ImageTensorParams

    def __init__(self, config: DatasetConfig):
        super().__init__(config=config)
        self._params = ImageTensorParams(self._config.params)
        # If no target is specified, set it to the default target for image classification.
        roles = self._metadata.roles
        if RoleName.TARGET not in roles or len(roles[RoleName.TARGET]) == 0:
            roles = self._metadata.roles
            # TODO(Merritt): plugins should have thier own defaults & constants
            roles[RoleName.TARGET] = [Column(name=Defaults.IMAGE_CLF_TARGET_NAME)]
            self._metadata = self._metadata.override_roles(roles=roles)

    def validate(self, dataset: Optional[Dataset]) -> None:
        errors: List[ConfigError] = []

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)

    def _load_train(self) -> Dataset:
        train_ds = tf.keras.utils.image_dataset_from_directory(
            self._params.train_dir,
            validation_split=float(self._params.validation_split),
            subset="training",
            seed=self._params.seed,
            image_size=(int(self._params.img_height),
                        int(self._params.img_width)),
            batch_size=int(self._params.batch_size)
        )

        val_ds = tf.keras.utils.image_dataset_from_directory(
            self._params.train_dir,
            validation_split=float(self._params.validation_split),
            subset="validation",
            seed=self._params.seed,
            image_size=(int(self._params.img_height),
                        int(self._params.img_width)),
            batch_size=int(self._params.batch_size)
        )
        dataset = Dataset(
            metadata=self._metadata,
            keras_ds=train_ds,
            keras_validate=val_ds
        )

        return dataset

    def _load_test(self) -> Optional[Dataset]:
        test_ds = tf.keras.utils.image_dataset_from_directory(
            self._params.test_dir,
            labels=None,
            seed=self._params.seed,
            image_size=(int(self._params.img_height),
                        int(self._params.img_width)),
            batch_size=int(self._params.batch_size),
            shuffle=False
        )

        dataset = Dataset(
            metadata=self._metadata,
            keras_ds=test_ds
        )
        return dataset

    def _load_ground_truth(self) -> Optional[Dataset]:
        return None

    def _dataset(self, data: Any, **kwargs) -> Dataset:
        # TODO(Merritt): implement this
        raise NotImplementedError

    def poll(self, timeout: Optional[float] = 0.0) -> Optional[Dataset]:
        return self.load_train()

    def build_dataset_from_json(self, json_data: Dict) -> Dataset:
        # TODO(Piggy): implement this
        raise NotImplementedError


def register(catalog: DataLoaderCatalog, *unused_args, **unused_kwargs):
    '''Register all the objects in this file.'''
    catalog.register(ImageTensorDataLoader)
