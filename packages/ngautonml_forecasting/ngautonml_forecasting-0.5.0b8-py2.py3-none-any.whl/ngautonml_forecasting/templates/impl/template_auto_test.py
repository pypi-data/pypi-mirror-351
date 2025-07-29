'''Test the autoloading template catalog.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

from glob import glob
from pathlib import Path
import subprocess

from ngautonml.templates.impl.parallel_step import ParallelStep
from ngautonml.templates.impl.pipeline_template import PipelineTemplate
from ngautonml.templates.impl.query_step import QueryStep
from ngautonml.templates.impl.template_auto import TemplateCatalogAuto

# pylint: disable=missing-function-docstring,duplicate-code


def test_forecasting() -> None:
    plugin_root = Path(__file__).parents[3]
    subprocess.run(['python', '-m', 'build'], cwd=plugin_root, check=True)

    pluginpaths = glob(str(plugin_root / 'dist' / 'ngautonml_forecasting-*py3-none-any.whl'))
    assert len(pluginpaths) == 1, f'BUG: unexpected extra whl files: {pluginpaths}'
    pluginpath = Path(pluginpaths[0])
    subprocess.run(['pip', 'install', '--no-input', pluginpath], check=True)
    dut = TemplateCatalogAuto()
    forecasting_pipes = dut.lookup_by_task(task='forecasting')
    assert 'forecasting' in forecasting_pipes
    forecasting = forecasting_pipes['forecasting']
    assert isinstance(forecasting.steps[0], ParallelStep)
    subpipe_keys = sorted(list(forecasting.steps[0].subpipeline_keys))
    assert ['static', 'timeseries'] == subpipe_keys
    timeseries_subpipe = forecasting.steps[0].subpipeline(key='timeseries')
    assert isinstance(timeseries_subpipe, PipelineTemplate)
    assert isinstance(timeseries_subpipe.steps[3], ParallelStep)
    assert isinstance(forecasting.steps[2], QueryStep)
    subprocess.run(['pip', 'uninstall', '-y', pluginpath], check=True)
