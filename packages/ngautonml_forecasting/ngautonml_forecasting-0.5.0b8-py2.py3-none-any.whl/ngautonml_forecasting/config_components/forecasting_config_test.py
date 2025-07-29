'''Tests for forecasting_config.py'''

# Copyright (c) 2024 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=missing-function-docstring,protected-access,duplicate-code

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Tuple, Type

import pandas as pd
import pytest

from ngautonml.config_components.dataset_config import DatasetConfig
from ngautonml.data_loaders.impl.data_loader import DataLoader
from ngautonml.data_loaders.impl.data_loader_auto import DataLoaderCatalogAuto
from ngautonml.data_loaders.local_data_loader import LocalDataLoader
from ngautonml.data_loaders.memory_data_loader import MemoryDataLoader
from ngautonml.problem_def.problem_def import ProblemDefinition, ValidationErrors
from ngautonml.tables.impl.table_auto import TableCatalogAuto

from .forecasting_config import ForecastingConfig
_ = TableCatalogAuto()


def valid_csv(filename: Optional[str] = None) -> str:
    '''Returns a path (in the form of a string) to a valid csv file.'''
    module_parent = Path(__file__).parents[4]
    if filename is None:
        filename = 'all_stocks_5yr.csv'
    path = module_parent / 'examples' / 'forecasting' / filename
    return str(path)


FORECASTING_PROBLEM_DEF: Dict[str, Any] = {
    'dataset': {
        'config': 'local',
        'column_roles': {
            'target': {
                'name': 'open'
            },
            'time': {
                'name': 'date'
            },
            'timeseries_id': {
                'name': 'Name'
            }
        }
    },
    'forecasting': {
        'horizon': 5,
        'input_size': 15,
        'frequency': 'ME'
    },
    'problem_type': {
        'task': 'forecasting'
    }
}


def mk_local() -> ProblemDefinition:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['params'] = {
        'train_path': valid_csv(),
        'test_path': valid_csv()
    }

    return ProblemDefinition(clause)


def mk_memory() -> ProblemDefinition:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['config'] = 'memory'
    clause['dataset']['params'] = {
        'train_data': 'train_df',
        'test_data': 'test_df'
    }

    return ProblemDefinition(clause=clause)


def get_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.DataFrame({
        'open': [1] * 10,
        'date': [1] * 10,
        'Name': [1] * 10
    })
    return (df.copy(), df.copy())


@pytest.mark.parametrize("mkdut,loader_class", [
    (mk_local, LocalDataLoader),
    (mk_memory, MemoryDataLoader),
])
def test_forecasting_metadata(mkdut: Callable[[], ProblemDefinition],
                              loader_class: Type[DataLoader]) -> None:
    (train_df, test_df) = get_data()  # noqa: F841 pylint: disable=unused-variable
    dut = mkdut().get_conf(ProblemDefinition.Keys.DATASET)
    assert isinstance(dut, DatasetConfig)
    loader = DataLoaderCatalogAuto().construct_instance(config=dut)
    assert isinstance(loader, loader_class)
    dataset = loader.load_train()
    assert dataset is not None
    forecasting_config = dataset.metadata.get_conf('forecasting')
    assert isinstance(forecasting_config, ForecastingConfig)
    assert forecasting_config.horizon == 5
    assert forecasting_config.input_size == 15
    assert forecasting_config.frequency == 'ME'
    assert forecasting_config.step_size == 5


@pytest.mark.parametrize("mkdut,loader_class", [
    (mk_local, LocalDataLoader),
    (mk_memory, MemoryDataLoader),
])
def test_load_testdata_forecasting(mkdut: Callable[[], ProblemDefinition],
                                   loader_class: Type[DataLoader]) -> None:
    # check that we don't drop the target column for forecasting test data
    (train_df, test_df) = get_data()  # noqa: F841 pylint: disable=unused-variable
    dut = mkdut().get_conf(ProblemDefinition.Keys.DATASET)
    assert isinstance(dut, DatasetConfig)
    loader = DataLoaderCatalogAuto().construct_instance(config=dut)
    assert isinstance(loader, loader_class)
    test_data = loader.load_test()
    assert test_data is not None
    assert 'open' in test_data.dataframe_table.columns


def test_forecasting_step_size() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    clause['forecasting']['step_size'] = 3
    dataset_config = ProblemDefinition(clause).get_conf(ProblemDefinition.Keys.DATASET)
    assert isinstance(dataset_config, DatasetConfig)
    dut = DataLoaderCatalogAuto().construct_instance(config=dataset_config)
    assert isinstance(dut, LocalDataLoader)
    dataset = dut.load_train()
    assert dataset is not None
    forecasting_config = dataset.metadata.get_conf('forecasting')
    assert isinstance(forecasting_config, ForecastingConfig)
    assert forecasting_config.step_size == 3


def test_forecasting_invalid_step_size() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    clause['forecasting']['step_size'] = 8

    with pytest.raises(ValidationErrors, match=r"step_size"):
        ProblemDefinition(clause)


def test_static_exog() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    clause['dataset']['test_path'] = valid_csv()
    clause['dataset']['static_exogenous_path'] = valid_csv()
    dataset_config = ProblemDefinition(clause).get_conf(ProblemDefinition.Keys.DATASET)
    assert isinstance(dataset_config, DatasetConfig)
    dut = DataLoaderCatalogAuto().construct_instance(config=dataset_config)
    got = dut.load_train()
    assert got is not None
    assert isinstance(got['static_exogenous'], pd.DataFrame)
    got_test = dut.load_test()
    assert got_test is not None
    assert isinstance(got_test['static_exogenous'], pd.DataFrame)
    pd.testing.assert_frame_equal(got['static_exogenous'], got_test['static_exogenous'])


def test_static_exog_missing() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    clause['dataset']['test_path'] = valid_csv()

    dataset_config = ProblemDefinition(clause).get_conf(ProblemDefinition.Keys.DATASET)
    assert isinstance(dataset_config, DatasetConfig)
    dut = DataLoaderCatalogAuto().construct_instance(config=dataset_config)
    got = dut.load_train()
    assert got is not None
    assert got.static_exogenous_table is None

    got_test = dut.load_test()
    assert got_test is not None
    assert got_test.static_exogenous_table is None


FORECASTING_NO_TIME = '''{
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "target": {
                "name": "class"
            }
        }
    },
    "forecasting": {
        "horizon": 5,
        "input_size": 15
    },
    "problem_type": {
        "task": "forecasting"
    }
}
'''


def test_forecasting_no_time() -> None:
    with pytest.raises(ValidationErrors,
                       match='(?i)(forecasting.*time)|(time.*forecasting)'):
        ProblemDefinition(FORECASTING_NO_TIME)


FORECASTING_NO_HORIZON = {
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "target": {
                "name": "class"
            },
            "time": {
                "name": "FOO"
            }
        },
    },
    "forecasting": {
        "input_size": 15
    },
    "problem_type": {
        "task": "forecasting"
    }
}


def test_forecasting_no_horizon() -> None:
    with pytest.raises(ValidationErrors, match='horizon'):
        ProblemDefinition(FORECASTING_NO_HORIZON)


FORECASTING_INVALID_FREQUENCY = '''{
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "target": {
                "name": "class"
            },
            "time": {
                "name": "FOO"
            }
        }
    },
    "forecasting": {
        "horizon": 5,
        "input_size": 15,
        "frequency": "INVALID_FREQ_FOR_TEST"
    },
    "problem_type": {
        "task": "forecasting"
    }
}
'''


def test_forecasting_invalid_frequency() -> None:
    with pytest.raises(ValidationErrors,
                       match='(forecasting.*frequency)|(frequency.*forecasting)'):
        ProblemDefinition(FORECASTING_INVALID_FREQUENCY)


FORECASTING_WITH_FREQUENCY = '''{
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "target": {
                "name": "class"
            },
            "time": {
                "name": "FOO"
            }
        }
    },
    "forecasting": {
        "horizon": 5,
        "input_size": 15,
        "frequency": "D"
    },
    "problem_type": {
        "task": "forecasting"
    }
}
'''


def test_forecasting_with_frequency() -> None:
    dut = ProblemDefinition(FORECASTING_WITH_FREQUENCY)
    got = dut._get('forecasting', 'frequency')
    want = 'D'

    assert got == want


def test_forecast_no_clause() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    del clause['forecasting']

    with pytest.raises(ValidationErrors,
                       match=r'(?i)(forecasting.*not present)|(not present.*forecasting)'):
        ProblemDefinition(clause)


def test_forecast_clause_wrong_task_type() -> None:
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['problem_type']['task'] = 'regression'
    clause['dataset']['train_path'] = valid_csv()

    with pytest.raises(ValidationErrors, match=r'(?i)forecasting.*clause present for.*regression'):
        ProblemDefinition(clause)


def test_not_forecast_no_clause() -> None:
    '''We expect this case to not throw an error.'''
    clause = deepcopy(FORECASTING_PROBLEM_DEF)
    clause['dataset']['train_path'] = valid_csv()
    clause['problem_type']['task'] = 'regression'
    del clause['forecasting']
    ProblemDefinition(clause)
