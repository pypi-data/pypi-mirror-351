'''Class for Keras Sequential model'''
# pylint: disable=duplicate-code,too-many-arguments
from typing import Any, Dict, Iterable, List, Optional

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import numpy as np
import tensorflow as tf
import keras  # type: ignore[import-untyped]
from keras import layers  # type: ignore[import-untyped]
from ngautonml.algorithms.impl.fittable_algorithm_instance import (FittableAlgorithmInstance,
                                                                   UntrainedError)
from ngautonml.algorithms.impl.algorithm import Algorithm, MemoryAlgorithmCatalog
from ngautonml.catalog.catalog import upcast
from ngautonml.problem_def.task import DataType, TaskType
from ngautonml.wrangler.dataset import Dataset, DatasetKeys, TableFactory


class SequentialInstance(FittableAlgorithmInstance):
    '''This is an example image classifier using TensorFlow.

    https://www.tensorflow.org/tutorials/images/classification#compile_the_model
    '''
    _hyperparams: Dict[str, Any]
    _constructor: Any
    _class_names: List[str]
    _impl: Optional[keras.Sequential]

    def __init__(self, **overrides: Any):
        parent = overrides.pop('parent')
        self._constructor = keras.Sequential
        super().__init__(parent=parent)
        self._hyperparams = self.algorithm.hyperparams(**overrides)
        self._impl = None

    def hyperparams(self, **overrides) -> Dict[str, Any]:
        '''Report hyperparams with the ability to override them.'''
        retval = self._hyperparams.copy()
        retval.update(overrides)
        return retval

    def _mk_model(self, **overrides) -> keras.Sequential:
        params = self.algorithm.hyperparams(**overrides)
        print(params)
        return keras.Sequential([
            layers.Rescaling(1. / 255, input_shape=(params['img_height'], params['img_width'], 3)),
            layers.Conv2D(16, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(32, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Conv2D(64, 3, padding='same', activation='relu'),
            layers.MaxPooling2D(),
            layers.Flatten(),
            layers.Dense(128, activation='relu'),
            layers.Dense(params['num_classes'])
        ])

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit the model.'''
        if dataset is None:
            return
        params = self.hyperparams()
        train_ds = dataset[DatasetKeys.KERAS_DS.value]
        assert isinstance(train_ds, tf.data.Dataset)
        val_ds = dataset[DatasetKeys.KERAS_VALIDATE.value]
        assert isinstance(val_ds, tf.data.Dataset)

        self._class_names = train_ds.class_names
        if params['num_classes'] is None:
            params['num_classes'] = len(self._class_names)
        self._impl = self._mk_model(**params)
        self._impl.compile(
            optimizer=self.hyperparams()['optimizer'],
            loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=['accuracy'])

        # Grab the epochs to pass to fit
        epochs = self.hyperparams()['epochs']

        # unsure why this was in a try/except
        self._impl.fit(train_ds,
                       validation_data=val_ds,
                       epochs=epochs)
        self._trained = True

    def predict(self, dataset: Optional[Dataset]) -> Optional[Dataset]:
        # TODO(Merritt): we should get train predictions somehow
        if not self._trained:
            raise UntrainedError(f'attempt to predict before fit for {self.catalog_name}')

        if dataset is None:
            return None

        assert self._impl is not None

        predictions = self._impl.predict(dataset[DatasetKeys.KERAS_DS.value])
        assert isinstance(predictions, np.ndarray)
        scores: Iterable[tf.Tensor] = tf.nn.softmax(predictions)
        prediction_result: List[str] = [self._class_names[np.argmax(score)] for score in scores]

        retval = dataset.output()

        assert dataset.metadata.target is not None

        retval.predictions_table = TableFactory({
            dataset.metadata.target.name: prediction_result
        })

        return retval


class KerasSequential(Algorithm):
    '''Class for Keras Sequential model'''
    _name = 'tf.keras.sequential'
    _tags = {
        'data_type': [DataType.IMAGE.name],
        'task': [TaskType.BINARY_CLASSIFICATION.name,
                 TaskType.MULTICLASS_CLASSIFICATION.name],
        'for_tests': ['true']
    }
    _default_hyperparams = {
        'img_height': 128,
        'img_width': 128,
        'num_classes': None,
        'optimizer': 'adam',
        'epochs': 2,
    }
    _instance_constructor = SequentialInstance


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = KerasSequential(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
