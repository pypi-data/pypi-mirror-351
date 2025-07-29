'''Tests for AutoNHITS.py'''
# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=invalid-name, missing-function-docstring, duplicate-code
import warnings

from neuralforecast.utils import AirPassengersDF  # type: ignore[import]

import pandas as pd
from pytorch_lightning.utilities.warnings import PossibleUserWarning
import pytest
import torch

from ngautonml.problem_def.problem_def import ProblemDefinition
from ngautonml.tables.impl.table_auto import TableCatalogAuto
from ngautonml.wrangler.dataset import Column, Dataset, TableFactory, Metadata, RoleName
from .AutoNHITS import AutoNHITSModel
TableCatalogAuto()


PROBLEM_DEF = {
    'dataset': {
        'config': 'ignore',
        'column_roles': {
            'time': {'name': 'ds'},
        }
    },
    'problem_type': {
        'task': 'forecasting'
    },
    'forecasting': {
        'horizon': 12,
        'input_size': 24,
        'frequency': 'ME'
    }
}


def test_sunny_day() -> None:
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=PossibleUserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    if not torch.cuda.is_available():
        print('test disabled due to lack of GPU.')
        return

    model = AutoNHITSModel(num_samples=2)
    dut = model.instantiate()

    AirPassengersCovariates = AirPassengersDF[['unique_id', 'ds']]
    AirPassengersTarget = AirPassengersDF[['y']]

    metadata = Metadata(
        problem_def=ProblemDefinition(PROBLEM_DEF),
        roles={
            RoleName.TIMESERIES_ID: [Column('unique_id')],
            RoleName.TIME: [Column('ds')],
            RoleName.TARGET: [Column('y')]
        })
    dataset = Dataset(metadata=metadata)
    dataset.covariates_table = TableFactory(AirPassengersCovariates)
    dataset.target_table = TableFactory(AirPassengersTarget)
    dut.fit(dataset)

    got = dut.predict(dataset)

    first = got.predictions.head(n=1)
    assert first['ds'][0] == pd.Timestamp('1961-01-31 00:00:00')
    assert first['y'][0] == pytest.approx(451.5, 3)
