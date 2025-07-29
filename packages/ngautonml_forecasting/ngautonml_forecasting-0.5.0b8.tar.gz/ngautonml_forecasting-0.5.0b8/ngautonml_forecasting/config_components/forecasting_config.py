'''Config for the forecasting plugin.

This will move to the plugin when we add plugin support for ConfigComponent.
'''

from typing import Any, Dict, List, Optional

import pandas as pd

from ngautonml.config_components.dataset_config import DatasetConfig
from ngautonml.config_components.impl.config_component_catalog import ConfigComponentCatalog
from ngautonml.config_components.impl.config_component import (
    ConfigComponent, ConfigError, ValidationErrors, InvalidValueError,
    MissingKeyError)
from ngautonml.problem_def.problem_def_interface import ProblemDefInterface
from ngautonml.problem_def.task import TaskType
from ngautonml.wrangler.dataset import RoleName


class ForecastingConfig(ConfigComponent):
    '''Config component to store forecasting-related metadata'''
    name = 'forecasting'
    tags: Dict[str, List[str]] = {}

    def validate(self, problem_def: Optional[ProblemDefInterface] = None, **kwargs: Any) -> None:
        assert problem_def is not None, (
            'BUG: ForecastingConfig made without a problem def.')

        if problem_def.task.task_type != TaskType.FORECASTING:
            if not self._clause:
                return
            raise ValidationErrors([
                InvalidValueError(
                    '"forecasting" clause present for '
                    f'{problem_def.task.task_type.name} problem.')])
        if not self._clause:
            raise ValidationErrors([
                MissingKeyError(
                    '"forecasting" clause not present for forecasting problem.')])

        errors: List[ConfigError] = []

        try:
            self._get('horizon')

            # Only do this test if we have a horizon.
            if self.step_size < 1 or self.step_size > self.horizon:
                errors.append(InvalidValueError(
                    'Invalid value in forecasting metadata: '
                    f'{self.step_size} is not a valid value for step_size. '
                    f'Value for step_size must be between 1 and horizon ({self.horizon})'
                ))
        except ConfigError as err:
            errors.append(err)

        assert problem_def is not None, (
            "BUG: forecasting plugin validate called without problem_def.")
        dataset_config = problem_def.get_conf(problem_def.Keys.DATASET)
        assert isinstance(dataset_config, DatasetConfig)
        if RoleName.TIME not in dataset_config.metadata.roles:
            errors.append(MissingKeyError('Forecasting problem requires time column.'))
        else:
            time_cols = dataset_config.metadata.roles[RoleName.TIME]
            if len(time_cols) != 1:
                errors.append(InvalidValueError(
                    f'Forecasting time role is not unique: {time_cols}'))

        offset_strs = [x for x in dir(pd.offsets) if _is_valid_offset(x)]
        allowed_freq = [getattr(pd.offsets, x)().freqstr for x in offset_strs]
        if self.frequency not in allowed_freq:
            errors.append(InvalidValueError(
                'Invalid value in forecasting metadata: '
                f'{self.frequency} is not a valid value for frequency. '
                f'Allowed frequency values are: {allowed_freq}'))

        if len(errors) > 0:
            raise ValidationErrors(errors=errors)

    @property
    def horizon(self) -> int:
        '''Number of future data points to predict'''
        return int(self._get('horizon'))

    @property
    def input_size(self) -> int:
        '''Minimum number of past data points necessary to predict one horizon.

        Currently defaults to 2*horizon.
        '''
        # TODO(Merritt): this is a hack and a more intelligent default should be used
        return int(self._get_with_default('input_size', dflt=2 * self.horizon))

    @property
    def step_size(self) -> int:
        '''Interval of data points between the start of each window.

        Defaults to horizon (in which case the windows will cover each data
        point exactly once).
        '''
        return int(self._get_with_default('step_size', dflt=self.horizon))

    @property
    def frequency(self) -> str:
        '''The frequency of the time series.

        Chosen from the list of `pandas offset aliases <https://pandas.
        pydata.org/pandas-docs/stable/user_guide/timeseries.html#offset-aliases>`_
        '''
        return self._get_with_default('frequency', dflt='ME')


def _is_valid_offset(offset: str) -> bool:
    invalid_offsets = set(['BaseOffset', 'Tick', 'DateOffset', 'Easter'])
    obj = getattr(pd.offsets, offset)

    return not offset.startswith('_') and callable(obj) and offset not in invalid_offsets


def register(catalog: ConfigComponentCatalog) -> None:
    '''Register all the objects in this file.'''
    catalog.register(ForecastingConfig)
