'''An AutonML implementation of neuralforecast.models.NHITS'''
# pylint: disable=invalid-name, duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import neuralforecast as nf  # type: ignore[import]
from neuralforecast.losses.pytorch import MAE  # type: ignore[import]
from neuralforecast.models import NHITS  # type: ignore[import]

from ngautonml.algorithms.impl.algorithm import MemoryAlgorithmCatalog
from ngautonml.catalog.catalog import upcast
from ngautonml.problem_def.task import TaskType, DataType

from .neuralforecast_model import NeuralForecastModel, NeuralForecastModelInstance


class NHITSModelInstance(NeuralForecastModelInstance):
    '''Wrapper for neuralforecast.models.NHITS'''
    _impl: nf.core.NeuralForecast
    _constructor = NHITS


class NHITSModel(NeuralForecastModel):
    '''Wrapper for neuralforecast.models.NHITS

    The Neural Hierarchical Interpolation for Time Series (NHITS), is
    an MLP-based deep neural architecture with backward and forward
    residual links. NHITS tackles volatility and memory complexity
    challenges, by locally specializing its sequential predictions
    into the signals frequencies with hierarchical interpolation and
    pooling.

    .. rubric:: Required Parameters:

    * ``h``: ``int``, Forecast horizon.
    * ``input_size``: ``int``, autorregresive inputs size,
      ``y=[1,2,3,4] input_size=2 -> y_[t-2:t]=[1,2]``.

    .. rubric:: Hyperparams:

    * ``stat_exog_list``: ``str list``, static exogenous columns.
    * ``hist_exog_list``: ``str list``, historic exogenous columns.
    * ``futr_exog_list``: ``str list``, future exogenous columns.
    * ``exclude_insample_y``: ``bool=False``, the model skips the autoregressive
      features y[t-input_size:t] if True.
    * ``activation``: ``str``, activation from ``['ReLU', 'Softplus', 'Tanh',
      'SELU', 'LeakyReLU', 'PReLU', 'Sigmoid']``.
    * ``stack_types``: ``List[str]``, stacks list in the form ``N * [identity]``,
      to be deprecated in favor of n_stacks. Note that
      ``len(stack_types)=len(n_freq_downsample)=len(n_pool_kernel_size)``.
    * ``n_blocks``: ``List[int]``, Number of blocks for each stack. Note that
      ``len(n_blocks) = len(stack_types)``.
    * ``mlp_units``: ``List[List[int]]``, Structure of hidden layers for each
      stack type. Each internal list should contain the number of units
      of each hidden layer. Note that ``len(n_hidden) = len(stack_types)``.
    * ``n_freq_downsample``: ``List[int]``, list with the stack's coefficients
      (inverse expressivity ratios). Note that
      ``len(stack_types)=len(n_freq_downsample)=len(n_pool_kernel_size)``.
    * ``interpolation_mode``: ``str='linear'``, interpolation basis from
      ``['linear', 'nearest', 'cubic']``.
    * ``n_pool_kernel_size``: ``List[int]``, list with the size of the windows
      to take a max/avg over. Note that
      ``len(stack_types)=len(n_freq_downsample)=len(n_pool_kernel_size)``.
    * ``pooling_mode``: ``str``, input pooling module from ``['MaxPool1d', 'AvgPool1d']``.
    * ``dropout_prob_theta``: ``float``, Float between ``(0, 1)``. Dropout for NHITS basis.
    * ``loss``: PyTorch module, instantiated train loss class from ``losses`` collection.
    * ``valid_loss``: PyTorch module = ``loss``, instantiated valid loss class
      from ``losses`` collection.
    * ``max_steps``: ``int=1000``, maximum number of training steps.
    * ``learning_rate``: ``float=1e-3``, Learning rate between ``(0, 1)``.
    * ``num_lr_decays``: ``int=-1``, Number of learning rate decays, evenly
      distributed across ``max_steps``.
    * ``early_stop_patience_steps``: ``int=-1``, Number of validation iterations
      before early stopping.
    * ``val_check_steps``: ``int=100``, Number of training steps between every
      validation loss check.
    * ``batch_size``: ``int=32``, number of different series in each batch.
    * ``valid_batch_size``: ``int=None``, number of different series in each
      validation and test batch, if ``None`` uses ``batch_size``.
    * ``windows_batch_size``: ``int=1024``, number of windows to sample in each
      training batch, default uses all.
    * ``inference_windows_batch_size``: ``int=-1``, number of windows to sample
      in each inference batch, -1 uses all.
    * ``step_size``: ``int=1``, step size between each window of temporal data.
    * ``scaler_type``: ``str=`identity```, type of scaler for temporal inputs
      normalization see temporal scalers.
    * ``random_seed``: ``int``, ``random_seed`` for ``pytorch`` initializer and ``numpy``
      generators.
    * ``drop_last_loader``: ``bool=False``, if ``True`` ``TimeSeriesDataLoader`` drops
      last non-full batch.
    * ``alias``: ``str``, optional, Custom name of the model.
    * ``**trainer_kwargs``: ``int``, keyword trainer arguments inherited from
      PyTorch Lightning's trainer.
    '''
    _name = 'neuralforecast.models.NHITS'
    _basename = 'NHITS'
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
        'futr_exog_list': None,
        'hist_exog_list': None,
        'stat_exog_list': None,
        'stack_types': ['identity', 'identity'],
        'n_blocks': [1, 1, 1],
        'mlp_units': [[128, 128], [128, 128]],
        'n_pool_kernel_size': [1, 1],
        'n_freq_downsample': [1, 1],
        'pooling_mode': 'MaxPool1d',
        'interpolation_mode': 'linear',
        'dropout_prob_theta': 0.0,
        'activation': 'ReLU',
        'loss': MAE(),
        'valid_loss': None,
        'max_steps': 100,
        'learning_rate': 0.001,
        'num_lr_decays': 3,
        'early_stop_patience_steps': -1,
        'val_check_steps': 100,
        'batch_size': 32,
        'windows_batch_size': 16,
        'valid_batch_size': None,
        'step_size': 1,
        'scaler_type': 'identity',
        'drop_last_loader': False
    }
    _instance_constructor = NHITSModelInstance


def register(catalog: MemoryAlgorithmCatalog, *args, **kwargs) -> None:
    '''Register all the objects in this file.'''
    model = NHITSModel(*args, **kwargs)
    catalog.register(model, model.name, upcast(model.tags))
