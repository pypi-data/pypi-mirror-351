'''NGAutonML plugin for image classification.

Currently (10/25/2023) implemented using keras.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from pathlib import Path

from ngautonml.catalog.catalog import Catalog
from ngautonml.catalog.pathed_catalog import PathedCatalog


def templates_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin templates catalog.'''
    return PathedCatalog([Path(__file__).parent / 'templates'], **kwargs)


def algorithms_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin algorithms catalog.'''
    return PathedCatalog([Path(__file__).parent / 'algorithms'], **kwargs)


def data_loaders_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin data_loaders catalog.'''
    return PathedCatalog([Path(__file__).parent / 'data_loaders'], **kwargs)


def splitters_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin splitters catalog.'''
    return PathedCatalog([Path(__file__).parent / 'splitters'], **kwargs)
