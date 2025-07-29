'''An AutonML implementation of neuralforecast.models.NBEATS'''
# pylint: disable=invalid-name, duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import neuralforecast as nf  # type: ignore[import]
from neuralforecast.losses.pytorch import MAE  # type: ignore[import]
from neuralforecast.models import NBEATS  # type: ignore[import]

from ngautonml.algorithms.impl.algorithm import MemoryAlgorithmCatalog
from ngautonml.catalog.catalog import upcast
from ngautonml.problem_def.task import TaskType, DataType

from .neuralforecast_model import NeuralForecastModel, NeuralForecastModelInstance


class NBEATSModelInstance(NeuralForecastModelInstance):
    '''Wrapper for neuralforecast.models.NHITS'''
    _impl: nf.core.NeuralForecast
    _constructor = NBEATS


class NBEATSModel(NeuralForecastModel):
    '''Wrapper for neuralforecast.models.NBEATS

    The Neural Basis Expansion Analysis for Time Series (NBEATS), is a simple and yet effective
    architecture, it is built with a deep stack of MLPs with the doubly residual connections. It
    has a generic and interpretable architecture depending on the blocks it uses. Its
    interpretable architecture is recommended for scarce data settings, as it regularizes its
    predictions through projections unto harmonic and trend basis well-suited for most forecasting
    tasks.

    .. rubric:: Required Parameters:

    * ``h``: ``int``, Forecast horizon.
    * ``input_size``: ``int``, autorregresive inputs size,
      ``y=[1,2,3,4] input_size=2 -> y_[t-2:t]=[1,2]``.

    .. rubric:: Hyperparams:

    * ``n_harmonics``: ``int``, Number of harmonic terms for seasonality stack type. Note that
      ``len(n_harmonics) = len(stack_types)``. Note that it will only be used if a seasonality
      stack is used.
    * ``n_polynomials``: ``int``, polynomial degree for trend stack. Note that
      ``len(n_polynomials) = len(stack_types)``. Note that it will only be used if a trend
      stack is used.
    * ``stack_types``: ``List[str]``, List of stack types. Subset from ``['seasonality',
      'trend', 'identity']``.
    * ``n_blocks``: ``List[int]``, Number of blocks for each stack. Note that ``len(n_blocks) =
      len(stack_types)``.
    * ``mlp_units``: ``List[List[int]]``, Structure of hidden layers for each stack type. Each
      internal list should contain the number of units of each hidden layer. Note that
      ``len(n_hidden) = len(stack_types).``
    * ``dropout_prob_theta``: ``float``, Float between ``(0, 1)``. Dropout for N-BEATS basis.
    * ``shared_weights``: ``bool``, If ``True``, all blocks within each stack will share parameters.
    * ``activation``: ``str``, activation from ``['ReLU', 'Softplus', 'Tanh', 'SELU', 'LeakyReLU',
      'PReLU', 'Sigmoid']``.
    * ``loss``: PyTorch module, instantiated train loss class from losses collection.
    * ``valid_loss``: PyTorch module=``loss``, instantiated valid loss class from losses collection.
    * ``max_steps``: ``int=1000``, maximum number of training steps.
    * ``learning_rate``: ``float=1e-3``, Learning rate between ``(0, 1)``.
    * ``num_lr_decays``: ``int=3``, Number of learning rate decays, evenly distributed across
      max_steps.
    * ``early_stop_patience_steps``: ``int=-1``, Number of validation iterations before early
      stopping.
    * ``val_check_steps``: ``int=100``, Number of training steps between every validation loss
      check.
    * ``batch_size``: ``int=32``, number of different series in each batch.
    * ``valid_batch_size``: ``int=None``, number of different series in each validation and test
      batch, if None uses batch_size.
    * ``windows_batch_size``: ``int=1024``, number of windows to sample in each training batch,
      default uses all.
    * ``inference_windows_batch_size``: ``int=-1``, number of windows to sample in each inference
      batch, -1 uses all.
    * ``step_size``: ``int=1``, step size between each window of temporal data.
    * ``scaler_type``: ``str=identity``, type of scaler for temporal inputs normalization see
      temporal scalers.
    * ``random_seed``: ``int``, random_seed for pytorch initializer and numpy generators.
    * ``drop_last_loader``: ``bool=False``, if True TimeSeriesDataLoader drops last non-full batch.
    * ``alias``: ``str``, optional, Custom name of the model.
    * ``**trainer_kwargs``: ``int``, keyword trainer arguments inherited from
      PyTorch Lightning's trainer.
    '''
    _name = 'neuralforecast.models.NBEATS'
    _basename = 'NBEATS'
    _tags = {
        'task': [TaskType.FORECASTING.name],
        'data_type': [DataType.TIMESERIES.name],
        'for_tests': ['true'],
        'supports_random_seed': ['true'],
    }
    # TODO(Merritt/Piggy):
    #   These defaults are currently tuned for testing.
    #   When we introduce hyperparameter tuning, change them to better
    #   defaults for a real problem and use tuning in tests to set these hyperparams.
    _default_hyperparams = {
        'n_harmonics': 2,
        'n_polynomials': 2,
        'stack_types': ['identity', 'trend', 'seasonality'],
        'n_blocks': [1, 1, 1],
        'mlp_units': [[128, 128], [128, 128], [128, 128]],
        'dropout_prob_theta': 0.0,
        'activation': 'ReLU',
        'shared_weights': False,
        'loss': MAE(),
        'valid_loss': None,
        'max_steps': 100,
        'learning_rate': 0.001,
        'num_lr_decays': 3,
        'early_stop_patience_steps': -1,
        'val_check_steps': 100,
        'batch_size': 32,
        'valid_batch_size': None,
        'windows_batch_size': 16,
        'step_size': 1,
        'scaler_type': 'identity',
        'drop_last_loader': False
    }
    _instance_constructor = NBEATSModelInstance


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = NBEATSModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
