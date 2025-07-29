'''An AutonML implementation of neuralforecast.models.NHITS'''
# pylint: disable=invalid-name, duplicate-code

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

import abc
from typing import Any, Dict, Optional

import neuralforecast as nf  # type: ignore[import]
from neuralforecast.common._base_model import BaseModel  # type: ignore[import]
from pytorch_lightning import seed_everything
from ray import tune

from ngautonml.algorithms.impl.algorithm import Algorithm, AlgorithmCatalog
from ngautonml.algorithms.impl.algorithm_instance import DatasetError
from ngautonml.wrangler.dataset import Dataset

from ...config_components.forecasting_config import ForecastingConfig
from .neuralforecast_model import NeuralForecastModel, NeuralForecastModelInstance


class NeuralForecastAutoModel(NeuralForecastModel, metaclass=abc.ABCMeta):
    '''Base class for neuralforecast.auto.*'''
    _name: str = 'unnamed_neuralforecast_auto_model'


class NeuralForecastAutoModelInstance(NeuralForecastModelInstance):
    '''Wrapper for neuralforecast.auto.*'''
    _impl: nf.core.NeuralForecast
    _constructor: BaseModel  # BaseModel is the base class for all our neuralforecast models.
    _default_hyperparams: Dict[str, Any]

    def __init__(self, parent: Algorithm, **overrides: Any):
        super().__init__(parent=parent, **overrides)
        seed = self._default_hyperparams.pop('random_seed')
        seed_everything(seed)

    @property
    def _default_config(self):
        '''A hyperparameter for ray.tune that defines hyperparam search space'''
        # TODO(Merritt/Piggy):
        #   These defaults are currently tuned for testing.
        #   When we introduce hyperparameter tuning, change them to better
        #   defaults for a real problem and use tuning in tests to set these hyperparams.
        return {
            # Number of SGD steps
            "max_steps": 100,
            # Size of input window
            "input_size": 0,
            # Initial Learning rate
            "learning_rate": tune.loguniform(1e-5, 1e-1),
            # MaxPool's Kernelsize
            "n_pool_kernel_size": tune.choice([[2, 2, 2], [16, 8, 1]]),
            # Interpolation expressivity ratios
            "n_freq_downsample": tune.choice([[168, 24, 1], [24, 12, 1], [1, 1, 1]]),
            # Compute validation every 50 steps
            "val_check_steps": 50,
            # Random seed
            # TODO(Merritt/Piggy/Kin/Cristian): why is this picked randomly?
            "random_seed": tune.randint(1, 10),
        }

    def fit(self, dataset: Optional[Dataset]) -> None:
        '''Fit a model based on train data.

        Fit for neuralforecast auto models instantiates the model.
        '''
        if dataset is None:
            return
        # The next 4 lines are to work around a bug in
        # pytorch_lightning/utilities/parsing.py:_get_init_args.
        # TODO(piggy): Put a link to the pytorch_lightning bug here.
        parent = None
        parent = parent  # pylint: disable=self-assigning-variable
        overrides: Dict[str, Any] = {}
        overrides = overrides  # pylint: disable=self-assigning-variable

        ds = self._combine_and_rename(dataset=dataset)

        forecasting_metadata = dataset.metadata.get_conf('forecasting')
        assert isinstance(forecasting_metadata, ForecastingConfig), (
            f'BUG: "forecasting" config is of type {type(forecasting_metadata)}',
            'expected ForecastingConfig')

        hyperparams = self.hyperparams(h=forecasting_metadata.horizon)
        if hyperparams['config'] is None:
            hyperparams['config'] = self._default_config

        assert isinstance(hyperparams['config'], Dict)

        # set input size from metadata
        if forecasting_metadata.input_size is None:
            raise DatasetError(
                f'Attempt to fit {self._algorithm.name} on a dataset with no input_size metadata.')
        hyperparams['config']['input_size'] = forecasting_metadata.input_size

        models = [
            self._constructor(**hyperparams)
        ]
        self._impl = nf.NeuralForecast(models=models,
                                       freq=forecasting_metadata.frequency)
        try:
            self._impl.fit(df=ds.get_dataframe())
        except KeyError as err:
            raise DatasetError(f'fit dataset malformed {ds!r}') from err

        self._trained = True


def register(catalog: AlgorithmCatalog, *args, **kwargs) -> None:  # pylint: disable=unused-argument
    '''There are no objects in this file to register, but a register method is required.'''
