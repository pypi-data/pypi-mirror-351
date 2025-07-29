'''Pipeline template for a time series forecasting problem.'''

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# pylint: disable=too-many-arguments,duplicate-code

from typing import Dict, List, Optional

from ngautonml.algorithms.column_parser import ColumnParser
from ngautonml.algorithms.connect import ConnectorModel
from ngautonml.algorithms.extract_columns_by_role import ExtractColumnsByRoleModel
from ngautonml.algorithms.impl.algorithm import AlgorithmCatalog
from ngautonml.algorithms.sklearn.impute.simple_imputer import SimpleImputerModel
from ngautonml.algorithms.wide_to_long import WideToLongModel
from ngautonml.problem_def.task import DataType, TaskType
from ngautonml.templates.impl.pipeline_step import GeneratorInterface
from ngautonml.templates.impl.pipeline_template import PipelineTemplate
from ngautonml.templates.impl.template import TemplateCatalog
from ngautonml.wrangler.dataset import DatasetKeys, RoleName


class ForecastingTemplate(PipelineTemplate):
    '''Pipeline template for a time series forecasting problem.'''
    _tags: Dict[str, List[str]] = {
        'task': [TaskType.FORECASTING.name],
        'data_type': [DataType.TIMESERIES.name]
    }
    _name = 'forecasting'

    def __init__(self,
                 name: Optional[str] = None,
                 tags: Optional[Dict[str, List[str]]] = None,
                 algorithm_catalog: Optional[AlgorithmCatalog] = None,
                 generator: Optional[GeneratorInterface] = None):
        super().__init__(name=name or self._name,
                         tags=tags or self._tags,
                         algorithm_catalog=algorithm_catalog, generator=generator)

        # Extract```` static exogenous table in order to
        # ensure that none of the preprocessors operate on it
        static = self.new(name='static')
        static.step(
            model=ConnectorModel(),
            serialized_model=None,
            **{
                DatasetKeys.STATIC_EXOGENOUS_TABLE.value: DatasetKeys.STATIC_EXOGENOUS_TABLE.value
            }
        ).set_name('static_exogenous')

        # Extract all the dataset other than static exogenous,
        # run WideToLongModel on it,
        # then split out Attributes for imputing.
        timeseries = self.new(name='timeseries')
        timeseries.step(
            model=ConnectorModel(),
            serialized_model=None,
            **{
                DatasetKeys.DATAFRAME_TABLE.value: DatasetKeys.DATAFRAME_TABLE.value
            }
        ).set_name('strip_to_dataframe')
        timeseries.step(ColumnParser())
        timeseries.step(WideToLongModel())

        covariates = timeseries.new(name='covariates')
        covariates.step(
            model=ExtractColumnsByRoleModel(),
            desired_roles=[
                RoleName.TIME,
                RoleName.TIMESERIES_ID,
                RoleName.PAST_EXOGENOUS,
                RoleName.FUTURE_EXOGENOUS]).set_name('extract_columns_by_role_model:attribute')
        covariates.step(SimpleImputerModel()).set_name('simple_imputer')

        target = timeseries.new(name='target')
        target.step(
            model=ExtractColumnsByRoleModel(),
            desired_roles=RoleName.TARGET).set_name('extract_columns_by_role_model:target')

        timeseries.parallel(
            target_dataset=target, covariates_dataset=covariates).set_name(
                'parallel_target_covariates')
        self.parallel(
            timeseries=timeseries, static=static).set_name('parallel_timeseries_static')
        self.step(
            model=ConnectorModel(),
            serialized_model=None,
            **{
                DatasetKeys.TARGET_TABLE.value: [
                    'timeseries', 'target_dataset', DatasetKeys.DATAFRAME_TABLE.value],
                DatasetKeys.COVARIATES_TABLE.value: [
                    'timeseries', 'covariates_dataset', DatasetKeys.DATAFRAME_TABLE.value],
                DatasetKeys.STATIC_EXOGENOUS_TABLE.value: [
                    'static', DatasetKeys.STATIC_EXOGENOUS_TABLE.value]
            }
        ).set_name('timeseries_static_connector')

        self.query(task=TaskType.FORECASTING.name).set_name('forecaster')


def register(catalog: TemplateCatalog,
             algorithm_catalog: Optional[AlgorithmCatalog] = None,
             generator: Optional[GeneratorInterface] = None):
    '''Register all the objects in this file.'''
    catalog.register(ForecastingTemplate(algorithm_catalog=algorithm_catalog, generator=generator))
