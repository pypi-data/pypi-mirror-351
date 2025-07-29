'''Splitter for time series forecasting problems.'''
import logging

import pandas as pd

from ngautonml.problem_def.cross_validation_config import CrossValidationConfig
from ngautonml.problem_def.task import DataType, TaskType
from ngautonml.splitters.impl.splitter import (Fold, SplitDataset, Splitter,
                                               SplitterCatalog)
from ngautonml.wrangler.dataset import Dataset, RoleName, TableFactory

from ..config_components.forecasting_config import ForecastingConfig

# Copyright (c) 2023 Carnegie Mellon University
# This code is subject to the license terms contained in the LICENSE file.

# We favor standalone clarity over code unification for splitters.
# pylint: disable=duplicate-code, too-many-locals


class ForecastingSplitter(Splitter):
    '''Splitter for time series forecasting problems.'''
    _name = 'forecasting'
    _tags = {'task': [TaskType.FORECASTING.name],
             'data_type': [DataType.TABULAR.name,
                           DataType.TIMESERIES.name]}

    def split(self,
              dataset: Dataset,
              **unused_overrides) -> SplitDataset:
        '''Split dataset into ground_truth, train, and validation sets
        for time series forecasting problems.

        Generated fields are:

        * ``ground_truth`` is the last ``dataset_config.horizon`` entries of the dataset.
        * ``train`` is all entries that are not in ``ground_truth``.
        * ``validate`` is the last ``input_size`` entries of train (what is needed to predict
          values for ``ground_truth``)

        '''
        train = dataset.output()
        validate = dataset.output()
        ground_truth = dataset.output()

        forecasting_metadata = dataset.metadata.get_conf('forecasting')
        assert isinstance(forecasting_metadata, ForecastingConfig), (
            f'BUG: "forecasting" component is a {type(forecasting_metadata)},'
            ', exepcted a ForecastingConfig.')

        horizon = forecasting_metadata.horizon
        input_size = forecasting_metadata.input_size
        assert horizon is not None, (
            'BUG: forecasting splitter used without horizon metadata.')
        assert input_size is not None, (
            'BUG: forecasting splitter used without input size metadata.')

        data_df = dataset.get_dataframe()

        assert RoleName.TIME in dataset.roles, (
            'BUG: validation should have confirmed that '
            'there was a TIME role.')
        assert len(dataset.roles[RoleName.TIME]) == 1, (
            'BUG: validation should have confirmed that '
            f'there was only one time column. Got {dataset.roles[RoleName.TIME]!r} instead')

        time_colname = dataset.roles[RoleName.TIME][0].name
        assert time_colname is not None
        logging.info('forecasting_splitter sorting on column %s', time_colname)
        # Note: time column also gets parsed in column_parser.py
        # TODO(Merritt): remove this redundancy once it is no longer needed
        data_df[time_colname] = pd.to_datetime(data_df[time_colname])
        data_df.sort_values(by=str(time_colname), inplace=True)

        size = len(data_df)
        train_size = size - horizon

        # TODO(Merritt): do some checks to make sure that the number of rows are enough
        # TODO(Merritt): ground truth length should be horizon * number of time series in problem
        # (assuming long format)
        ground_truth_df = data_df.tail(n=horizon)
        train_df = data_df.head(n=train_size)  # equivalent: data_df.drop(ground_truth_df.index)
        validate_df = train_df.tail(n=input_size)

        ground_truth.ground_truth_table = TableFactory(ground_truth_df)
        train.dataframe_table = TableFactory(train_df)
        validate.dataframe_table = TableFactory(validate_df)

        train.static_exogenous_table = dataset.static_exogenous_table
        validate.static_exogenous_table = dataset.static_exogenous_table

        return SplitDataset([Fold(train=train, validate=validate, ground_truth=ground_truth)])


def register(catalog: SplitterCatalog, *args, cv_config: CrossValidationConfig, **kwargs):
    '''Register all the objects in this file.'''
    catalog.register(ForecastingSplitter(*args, cv_config=cv_config, **kwargs))
