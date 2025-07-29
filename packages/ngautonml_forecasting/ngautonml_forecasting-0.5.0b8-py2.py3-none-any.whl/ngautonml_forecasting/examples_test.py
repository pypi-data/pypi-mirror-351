'''Tests replicating example notebooks.'''
# pylint: disable=missing-function-docstring,missing-class-docstring

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from glob import glob
from pathlib import Path
import subprocess
import warnings

import pytest
from pytorch_lightning.utilities.warnings import PossibleUserWarning

from ngautonml.wrangler.wrangler import Wrangler
from ngautonml.problem_def.problem_def import ProblemDefinition
from ngautonml.algorithms.impl.algorithm_auto import FakeAlgorithmCatalogAuto
# pylint: disable=duplicate-code, redefined-outer-name


def module_path() -> Path:
    return Path(__file__).parents[3]


@pytest.fixture(scope="session")
def resource() -> str:
    plugin_root = Path(__file__).parents[1]

    subprocess.run(['python', '-m', 'build'], cwd=plugin_root, check=False)

    pluginpaths = glob(str(plugin_root / 'dist' / 'ngautonml_forecasting-*py3-none-any.whl'))
    assert len(pluginpaths) == 1, f'BUG: unexpected extra whl files: {pluginpaths}'
    pluginpath = Path(pluginpaths[0])
    subprocess.run(['pip', 'install', pluginpath], check=True)

    yield "plugin"

    subprocess.run(['pip', 'uninstall', '-y', pluginpath], check=False)


AIR_PASSENGERS_CONFIG = """
{{
    "dataset" : {{
        "config" : "local",
        "train_path" : "{train_path}",
        "test_path" : "{test_path}",
        "column_roles": {{
            "timeseries_id": {{
                "name": "unique_id"
            }},
            "time" : {{
                "name" : "ds"
            }},
            "target" : {{
                "name" : "y"
            }}
        }}
    }},
    "forecasting" : {{
        "horizon" : 5,
        "input_size" : 15,
        "frequency": "ME"
    }},
    "problem_type" : {{
        "data_type": "TIMESERIES",
        "task": "FORECASTING"
    }},
    "metrics" :  {{
        "root_mean_squared_error": {{}}
    }},
    "cross_validation": {{
        "k": 2
    }},
    "output" : {{}}
}}
"""


def air_passengers_config():
    train_path = module_path() / 'examples' / 'forecasting' / 'air-passengers-train.csv'
    test_path = module_path() / 'examples' / 'forecasting' / 'air-passengers-test.csv'
    pdef = AIR_PASSENGERS_CONFIG.format(train_path=train_path, test_path=test_path)
    return ProblemDefinition(pdef)


def test_wrangle_forecasting(resource: str) -> None:
    _ = resource
    warnings.filterwarnings("ignore", category=UserWarning)
    warnings.filterwarnings("ignore", category=PossibleUserWarning)
    warnings.filterwarnings("ignore", category=DeprecationWarning)

    problem_definition = air_passengers_config()
    dut = Wrangler(
        problem_definition=problem_definition,
        algorithm_catalog=FakeAlgorithmCatalogAuto
    )

    got = dut.fit_predict_rank()

    assert got.test_results is not None
    train_predictions = list(got.train_results.values())[0].prediction.predictions_table
    test_predictions = list(got.test_results.values())[0].prediction.predictions_table

    assert train_predictions.shape == (5, 5)
    assert test_predictions.shape == (5, 4)


def test_example_forecasting(tmp_path: Path, resource: str) -> None:
    _ = resource
    path = module_path() / 'examples' / 'forecasting' / 'air-passengers.json'
    csv_path = module_path() / 'examples' / 'forecasting' / 'air-passengers-train.csv'
    test_csv_path = module_path() / 'examples' / 'forecasting' / 'air-passengers-test.csv'
    with path.open() as file:
        pd_str = file.read()
    pd_paths_fixed = pd_str.replace(
        'ngautonml/examples/forecasting/air-passengers-train.csv',
        str(csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/forecasting/air-passengers-test.csv',
        str(test_csv_path)
    )
    pd_paths_fixed = pd_paths_fixed.replace(
        'ngautonml/examples/forecasting/air-passengers-output',
        str(tmp_path / 'output_dir')
    )
    ProblemDefinition(pd_paths_fixed)  # fails if example json is not valid
