"""Etl import/export file parser module."""


from typing import (
    List, Optional, Callable, Tuple, Any
)
from dataclasses import replace
from datetime import datetime
import pandas as pd
from tqdm import tqdm

from .model import (
    SeriesSettings,
    SeriesIterator,
    RESOURCE_COLUMN,
    TIMESTAMP_COLUMN,
    METRIC_COLUMN,
    render_timestamp_zulu,
    ParserRequestError,
    TIMESTAMP_COLUMN_NAMES,
)


def prepare_settings_dataframe(
    input_data: pd.DataFrame,
    settings: SeriesSettings
) -> SeriesSettings:
    """Validate and update the input settings by extracting metadata from a input Pandas DataFrame."""
    # timestamp specification
    fail_msg = (
        'Dataframe input requires either:\n'
        ' - an index of type DatetimeIndex\n'
        ' - a `timestamp_column` setting indicating a column\n'
        ' - a `timestamp_interval` setting to compute timestamps'
    )
    if isinstance(input_data.index, pd.DatetimeIndex):
        pass
    elif settings.timestamp_interval:
        pass
    else:
        if not settings.timestamp_column:
            for column_name in input_data.columns:
                if isinstance(column_name, str) and column_name.lower() in TIMESTAMP_COLUMN_NAMES:
                    settings = replace(settings, timestamp_column=column_name)
                break
        if settings.timestamp_column:
            if settings.timestamp_column not in input_data.columns:
                raise ParserRequestError(fail_msg)
        else:
            raise ParserRequestError(fail_msg)

    # resource specification
    fail_msg = (
        'Please specify a resource, either as \n'
        ' - a fixed `resource` setting\n'
        ' - a `resource_column` that indicates the column '
        '(or column level) containing the resource'
    )
    if settings.resource:
        if settings.key_by_resource(settings.resource) is None:
            raise ParserRequestError('specified resource not in filtered resources')
    elif settings.resource_column:
        fail_msg = (
            f'Specified invalid `resource_column`={settings.resource_column}.'
            ' This should be either:\n'
            ' - a column name in the input data\n'
            ' - a level in a multiindex column'
        )
        if settings.resource_column in input_data.columns:
            # resources specified in data ...
            pass
        elif isinstance(input_data.columns, pd.MultiIndex):
            if settings.resource_column in input_data.columns.names:
                pass
            else:
                raise ParserRequestError(fail_msg)
        else:
            raise ParserRequestError(fail_msg)
    elif RESOURCE_COLUMN in input_data.columns:
        # resources specified in data ...
        pass
    elif (
        isinstance(input_data.columns, pd.MultiIndex) and
        RESOURCE_COLUMN in input_data.columns.names
    ):
        pass
    else:
        raise ParserRequestError(fail_msg)

    if settings.resources is None:
        settings = replace(
            settings,
            resources=_extract_resources(input_data.columns, settings)
        )

    # metric name specification (column name by default)
    if settings.metric_column:
        fail_msg = (
            f'Specified invalid `metric_column`={settings.metric_column}.'
            ' This should be either:\n'
            ' - a column name in the input data\n'
            ' - a level in a multiindex column'
        )
        if settings.metric_column in input_data.columns:
            pass
        elif isinstance(input_data.columns, pd.MultiIndex):
            if settings.metric_column in input_data.columns.names:
                pass
            else:
                raise ParserRequestError(fail_msg)
        else:
            raise ParserRequestError(fail_msg)

    if settings.metrics is None:
        settings = replace(
            settings,
            metrics=_extract_metrics(input_data.columns, settings)
        )

    # value specification
    if settings.value_column:
        if settings.value_column not in input_data.columns:
            raise ParserRequestError(
                f'Specified invalid `value_column`={settings.value_column}.'
                ' This should be a column name in the input data'
            )
        if not settings.metric_column or METRIC_COLUMN in input_data.columns:
            raise ParserRequestError(
                f'When `value_column`={settings.value_column} is specified, '
                ' a `metric_column` should be specified too.'
            )
    return settings


def iter_timeseries_dataframe(
    *input_dataframes: pd.DataFrame,
    settings: SeriesSettings,
    progress: bool = False
) -> SeriesIterator:
    """Create a SeriesIterator from the given pandas Dataframe and settings."""
    if not input_dataframes:
        raise AttributeError('input required')
    if len(input_dataframes) > 1:
        raise AttributeError('input of multiple dataframes not yet supported')
    input_data = input_dataframes[0]
    settings = prepare_settings_dataframe(input_data, settings=settings)
    resource = settings.resource

    if settings.timestamp_interval:
        if not settings.timestamp_first and not settings.timestamp_last:
            settings.timestamp_last = datetime.utcnow()
        index = pd.date_range(
            start=settings.timestamp_first,
            end=settings.timestamp_last,
            periods=len(input_data.index),
            freq=settings.timestamp_interval,
        )
        index.name = TIMESTAMP_COLUMN
        input_data = input_data.set_index(index)
    else:
        if settings.timestamp_column:
            input_data = input_data.set_index(settings.timestamp_column)
            input_data.index.name = TIMESTAMP_COLUMN

        if settings.timestamp_constructor or not isinstance(input_data.index, pd.DatetimeIndex):
            index_series: pd.Series = input_data.index.to_series()
            input_data = input_data.reset_index(drop=True)
            if settings.timestamp_constructor:
                index_series = index_series.apply(settings.timestamp_constructor)
            if not isinstance(index_series, pd.DatetimeIndex):
                index_series = pd.DatetimeIndex(index_series)
            input_data.index = index_series

        offsets = [
            offset for offset in [
                settings.timestamp_offset,
                settings.timestamp_first - input_data.index[0]
                if settings.timestamp_first else None,
                settings.timestamp_last - input_data.index[-1]
                if settings.timestamp_last else None
            ]
            if offset
        ]
        if len(offsets) > 1:
            raise ParserRequestError(
                'To offset the timestamps for an ETL input, please specify only one of \n'
                ' - `timestamp_offset`\n'
                ' - `timestamp_first`\n'
                ' - `timestamp_last`\n'
            )
        if offsets:
            input_data = input_data.set_index(input_data.index + offsets[0])

        # assert correct tz info:
        if input_data.index.size > 0:
            first_ts = input_data.index[0]
            render_first_ts = render_timestamp_zulu(first_ts)

            if render_first_ts.endswith('Z'):
                pass
            elif '+' in render_first_ts:
                input_data = input_data.set_index(input_data.index.tz_convert('UTC'))
            elif settings.timestamp_timezone:
                index_series = input_data.index.tz_localize(settings.timestamp_timezone)
                index_series = index_series.tz_convert('UTC')
                input_data = input_data.set_index(index_series)
            else:
                raise ParserRequestError(
                    'Input data should contain (or have rules to convert to) UTC timestamps (including timezone info)\n'
                    f'  First timestamp: {first_ts}, rendered as {render_timestamp_zulu(first_ts)}\n'
                    'Please provide either:\n'
                    ' - a `timestamp_timezone` to interpret (local) timestamps to an UTC, e.g.\n'
                    '         timestamp_timezone="Europe/Brussels"\n'
                    ' - a `timestamp_constructor` to convert timestamps to an UTC timestamp, e.g.\n'
                    '         timestamp_constructor=lambda t: pd.Timestamp(t, tz="Europe/Brussels")\n'
                    ' - a `timestamp_first` or `timestamp_last` to shift the timestamps'
                )

    key_lambda = _column_key_extractor(input_data.columns, settings)
    if key_lambda is None:
        raise ParserRequestError('NOT YET SUPPORTED: variable resource and metric by row')
    if settings.value_column:
        column_series_iter = iter([
            (settings.value_column, input_data[settings.value_column])
        ])
        series_count = 1
    else:
        column_series_iter = input_data.items()
        series_count = len(input_data.columns)
    if progress and series_count > 1:
        with tqdm(total=series_count, unit_scale=True, unit_divisor=1, unit="series") as tqdm_progress:
            for column, series in column_series_iter:
                resource_column, metric_key = key_lambda(column)
                metric = settings.metric_by_key(metric_key)
                resource = settings.resource_by_key(resource_column)
                if resource and metric:
                    yield resource, metric, ((t, v) for t, v in series.items())
                    tqdm_progress.update(1)
    else:
        for column, series in column_series_iter:
            resource_column, metric_key = key_lambda(column)
            metric = settings.metric_by_key(metric_key)
            resource = settings.resource_by_key(resource_column)
            if resource and metric:
                yield resource, metric, ((t, v) for t, v in series.items())


def _column_key_extractor(columns, settings: SeriesSettings) -> Optional[Callable[[Any], Tuple[str, str]]]:
    default_resource = settings.resource
    if not isinstance(columns, pd.MultiIndex):
        if default_resource is None:
            if (
                settings.resource_column in columns or
                RESOURCE_COLUMN in columns
            ):
                return None  # different resource by row
            raise ParserRequestError('no resource specified')
        default_resource_id: str = default_resource
        if settings.metric_column in columns:
            return None  # different resource by row
        return lambda col: (default_resource_id, col)

    # multi index level containing the resource id
    resource_idx: int = next(
        (
            columns.names.index(resource_column)
            for resource_column in [
                settings.resource_column,
                RESOURCE_COLUMN
            ]
            if resource_column in columns.names
        ),
        -1
    )

    # multi index level containing the metric name
    metric_key_idx: int = next(
        (
            columns.names.index(resource_column)
            for resource_column in [
                settings.metric_column,
                METRIC_COLUMN,
                'name'
            ]
            if resource_column in columns.names
        ),
        -1
    )

    if resource_idx == -1:
        if default_resource is None:
            raise ParserRequestError('no resource specified')

        default_resource_str: str = default_resource
        if metric_key_idx == -1:
            # use all levels joined as metric name
            return lambda col: (default_resource_str, '-'.join(col))

        return lambda col: (default_resource_str, col[metric_key_idx])
    else:
        if metric_key_idx == -1:
            # use all levels joined as metric name (except the resource one)
            return lambda col: (col[resource_idx], '-'.join(col[:resource_idx]+col[(resource_idx+1):]))

        return lambda col: (col[resource_idx], col[metric_key_idx])


def _extract_resources(columns, settings) -> Optional[List[str]]:
    extractor = _column_key_extractor(columns, settings)
    if not extractor:
        return None

    return list({
        extractor(col)[0]: True
        for col in columns
        if col != settings.timestamp_column
    })


def _extract_metrics(columns, settings) -> Optional[List[str]]:
    extractor = _column_key_extractor(columns, settings)
    if not extractor:
        return None

    return list({
        extractor(col)[1]: True
        for col in columns
        if col != settings.timestamp_column
    })
