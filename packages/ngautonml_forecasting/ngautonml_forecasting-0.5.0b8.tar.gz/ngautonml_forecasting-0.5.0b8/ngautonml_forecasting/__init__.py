'''This is our test plugin for PluginCatalog.'''

from pathlib import Path

from ngautonml.catalog.catalog import Catalog
from ngautonml.catalog.pathed_catalog import PathedCatalog


def templates_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin templates catalog.'''
    return PathedCatalog([Path(__file__).parent / 'templates'], **kwargs)


def algorithms_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin algorithms catalog.'''
    return PathedCatalog([Path(__file__).parent / 'algorithms'], **kwargs)


def splitters_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin splitters catalog.'''
    return PathedCatalog([Path(__file__).parent / 'splitters'], **kwargs)


def config_components_make_catalog(**kwargs) -> Catalog:
    '''Make the plugin config components catalog.'''
    return PathedCatalog([Path(__file__).parent / 'config_components'], **kwargs)
