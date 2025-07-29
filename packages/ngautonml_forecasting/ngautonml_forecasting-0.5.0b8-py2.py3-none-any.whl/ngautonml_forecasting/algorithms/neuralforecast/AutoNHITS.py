'''An AutonML implementation of neuralforecast.models.NHITS'''
# pylint: disable=invalid-name, duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import os

import neuralforecast as nf  # type: ignore[import]
from neuralforecast.losses.pytorch import MAE  # type: ignore[import]
from neuralforecast.auto import AutoNHITS  # type: ignore[import]

import ray

from ngautonml.algorithms.impl.algorithm import MemoryAlgorithmCatalog
from ngautonml.catalog.catalog import upcast
from ngautonml.problem_def.task import TaskType, DataType
from ngautonml.wrangler.constants import Defaults

from .neuralforecast_auto_model import NeuralForecastAutoModel, NeuralForecastAutoModelInstance


class AutoNHITSModelInstance(NeuralForecastAutoModelInstance):
    '''Wrapper for neuralforecast.models.NHITS'''
    _impl: nf.core.NeuralForecast
    _constructor = AutoNHITS


class AutoNHITSModel(NeuralForecastAutoModel):
    '''Wrapper for neuralforecast.auto.AutoNHITS

    The Neural Hierarchical Interpolation for Time Series (NHITS), is
    an MLP-based deep neural architecture with backward and forward
    residual links. NHITS tackles volatility and memory complexity
    challenges, by locally specializing its sequential predictions
    into the signals frequencies with hierarchical interpolation and
    pooling.

    .. rubric:: Required Parameters:

    * ``h``: ``int``, Forecast horizon.

    .. rubric:: Hyperparams:

    * ``loss``: PyTorch module, instantiated train loss class from ``losses`` collection.
    * ``valid_loss``: PyTorch module = ``loss``, instantiated valid loss class from ``losses``
      collection.
    * ``config``: ``dict``, dictionary with ray.tune defined search space.
    * ``search_alg``: ``ray.tune.search`` variant, ``BasicVariantGenerator``, ``HyperOptSearch``,
      ``DragonflySearch``, ``TuneBOHB``. for details see ``tune.search``.
    * ``num_samples``: ``int`` number of hyperparameter optimization steps/samples.
    * ``cpus``: ``int``, number of cpus to use during optimization, default all available.
    * ``gpus``: ``int``, number of gpus to use during optimization, default all available.
    * ``refit_with_val``: ``bool=False``, whether refit of best model should preserve val size.
    * ``verbose``: ``bool``, whether to print partial outputs.
    * ``alias``: ``str``, optional, Custom name of the model.
    '''
    _name = 'neuralforecast.auto.AutoNHITS'
    _basename = 'AutoNHITS'
    _tags = {
        'task': [TaskType.FORECASTING.name],
        'data_type': [DataType.TIMESERIES.name],
        'supports_random_seed': ['true'],
    }
    # TODO(Merritt/Piggy):
    #   These defaults are currently tuned for testing.
    #   When we introduce hyperparameter tuning, change them to better
    #   defaults for a real problem and use tuning in tests to set these hyperparams.
    _default_hyperparams = {
        'loss': MAE(),
        'valid_loss': None,
        'config': None,
        # TODO(Piggy/Merritt): find a way to override the seed used here when user sets the seed
        'search_alg': ray.tune.search.basic_variant.BasicVariantGenerator(
            random_state=Defaults.SEED),
        'num_samples': 10,
        'refit_with_val': False,
        'cpus': os.cpu_count(),
        'gpus': 1,
        'verbose': False,
        'alias': None,
    }
    _instance_constructor = AutoNHITSModelInstance


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = AutoNHITSModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
