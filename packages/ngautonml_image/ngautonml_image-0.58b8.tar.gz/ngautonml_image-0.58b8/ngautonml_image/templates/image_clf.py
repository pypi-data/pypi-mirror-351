'''Pipeline template for image classification.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from typing import Dict, List, Optional

from ngautonml.algorithms.impl.algorithm import AlgorithmCatalog
from ngautonml.problem_def.task import DataType, TaskType
from ngautonml.templates.impl.pipeline_step import GeneratorInterface
from ngautonml.templates.impl.pipeline_template import PipelineTemplate
from ngautonml.templates.impl.template import TemplateCatalog


class ImageClassificationTemplate(PipelineTemplate):
    '''Pipeline template for image classification.'''
    _name = 'image_classifier'
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.BINARY_CLASSIFICATION.name,
                 TaskType.MULTICLASS_CLASSIFICATION.name],
        'data_type': [DataType.IMAGE.name],
    }

    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None):
        super().__init__(name=name or self._name,
                         tags=tags or self._tags,
                         algorithm_catalog=algorithm_catalog, generator=generator)
        self.query(
            task=[TaskType.BINARY_CLASSIFICATION.name,
                  TaskType.MULTICLASS_CLASSIFICATION.name],
            data_type=DataType.IMAGE.name).set_name('image_classifier')


def register(catalog: TemplateCatalog,
             algorithm_catalog: Optional[AlgorithmCatalog] = None,
             generator: Optional[GeneratorInterface] = None):
    '''Register all the objects in this file.'''
    catalog.register(
        ImageClassificationTemplate(
            algorithm_catalog=algorithm_catalog,
            generator=generator))
