'''Tests for neuralforecast_model.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=duplicate-code

import pytest
import pandas as pd

from ngautonml.algorithms.impl.algorithm import InputValueError
from ngautonml.tables.impl.table_auto import TableCatalogAuto
from ngautonml.wrangler.dataset import Dataset, Metadata, RoleName, Column, TableFactory

from .neuralforecast_model import NeuralForecastModel, NeuralForecastModelInstance
_ = TableCatalogAuto()


class FakeNeuralForecastModel(NeuralForecastModel):
    '''A fake neural forecast model for testing.'''

    def instantiate(self, **hyperparams) -> 'FakeNeuralForecastModelInstance':
        return FakeNeuralForecastModelInstance(parent=self, **hyperparams)


class FakeNeuralForecastModelInstance(NeuralForecastModelInstance):
    '''Empty'''


def test_fail_time_col_wrong_type() -> None:
    '''InputValueError should be raised if time column is not of datetime type.'''
    dut = FakeNeuralForecastModel().instantiate()

    cov = pd.DataFrame({'a': [1, 2], 'c': [5, 6]})
    targ = pd.DataFrame({'b': [3, 4]})
    dataset = Dataset(
        metadata=Metadata(
            roles={
                RoleName.TIME: [Column('a')],
                RoleName.TARGET: [Column('b')],
                RoleName.TIMESERIES_ID: [Column('c')]
            }
        )
    )
    dataset.covariates_table = TableFactory(cov)
    dataset.target_table = TableFactory(targ)

    with pytest.raises(InputValueError, match=r'(time.*int64)|(int64.*time)/i'):
        dut.fit(dataset=dataset)
