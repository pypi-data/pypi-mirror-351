'''Tests for forecasting.py'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from ngautonml.algorithms.impl.algorithm_auto import AlgorithmCatalogAuto
from ngautonml.generator.generator import GeneratorImpl
from ngautonml.problem_def.problem_def import ProblemDefinition
from .forecasting import ForecastingTemplate
# pylint: disable=missing-function-docstring,duplicate-code


FAKE_PROBLEM_DEF = '''{
    "output": {},
    "dataset": {
        "config": "ignore",
        "column_roles": {
            "time": {
                "name": "some_col"
            }
        }
    },
    "problem_type": {
        "task": "forecasting"
    },
    "forecasting": {
        "horizon": 5,
        "input_size": 10,
        "frequency": "ME"
    }
}
'''


def test_forecasting_template_generate() -> None:

    algorithm_catalog = AlgorithmCatalogAuto()
    generator = GeneratorImpl(
        algorithm_catalog=algorithm_catalog,
        problem_definition=ProblemDefinition(FAKE_PROBLEM_DEF))
    dut = ForecastingTemplate(algorithm_catalog=algorithm_catalog, generator=generator)

    bound_pipelines = generator.generate(pipeline=dut)
    assert len(bound_pipelines) >= 1
    assert 'forecasting@neuralforecast.models.nhits' in bound_pipelines.keys()
