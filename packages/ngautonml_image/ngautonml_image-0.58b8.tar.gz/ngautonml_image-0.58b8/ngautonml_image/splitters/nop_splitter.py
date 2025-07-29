'''Nop splitter that puts the entire dataset in TRAIN, and VALIDATE, and GROUND_TRUTH.'''

import numpy as np
import pandas as pd

from ngautonml.problem_def.cross_validation_config import CrossValidationConfig
from ngautonml.problem_def.task import DataType, TaskType
from ngautonml.splitters.impl.splitter import Splitter, SplitDataset, Fold, SplitterCatalog
from ngautonml.wrangler.dataset import Dataset, DatasetKeys, TableFactory


class NopSplitter(Splitter):
    '''Splitter that passes a dataset through unaltered.
    '''
    _name = 'nop'
    _tags = {
        'task': [
            TaskType.BINARY_CLASSIFICATION.name,
            TaskType.MULTICLASS_CLASSIFICATION.name
        ],
        'data_type': [DataType.IMAGE.name],
    }

    def split(self,
              dataset: Dataset,
              **unused_overrides) -> SplitDataset:
        '''Create a trivial SplitDataset with a single fold containing the entire dataset.

        A copy of the dataset gets put in TRAIN and VALIDATE for that fold,
        and a copy gets put in GROUND_TRUTH.
        '''

        val_ds = dataset[DatasetKeys.KERAS_VALIDATE.value]
        labels = np.concatenate([y for _, y in val_ds], axis=0)
        label_names = val_ds.class_names
        ground_truth_list = [label_names[label] for label in labels]
        assert dataset.metadata.target is not None
        ground_truth_df = pd.DataFrame(
            {dataset.metadata.target.name: ground_truth_list}
        )
        ground_truth_dataset = dataset.output()
        ground_truth_dataset.ground_truth_table = TableFactory(ground_truth_df)
        validate = dataset.output()
        validate[DatasetKeys.KERAS_DS.value] = val_ds
        return SplitDataset([Fold(train=dataset, validate=validate)])


def register(catalog: SplitterCatalog, *args, cv_config: CrossValidationConfig, **kwargs):
    '''Register all the objects in this file.'''
    catalog.register(NopSplitter(*args, cv_config=cv_config, **kwargs))
