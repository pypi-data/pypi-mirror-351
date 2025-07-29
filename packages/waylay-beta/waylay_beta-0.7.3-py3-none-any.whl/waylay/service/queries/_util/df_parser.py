from collections import OrderedDict
from collections.abc import Iterable
from typing import Union, TypeVar, Mapping, Tuple
import dataclasses

import pandas as pd
import numpy as np
import datetime
from pandas.core.base import PandasObject

from .parse_util import (
    to_iso_freq as tsa_to_iso_freq
)

RENDER_OPTION_KEYS = [
    RENDER_OPTION_ROLL_UP, RENDER_OPTION_HIERARCHICAL, RENDER_OPTION_VALUE_KEY,
    RENDER_OPTION_SHOW_LEVELS, RENDER_OPTION_ISO_TIMESTAMP,
    RENDER_OPTION_ROW_KEY, RENDER_OPTION_COLUMN_KEY, RENDER_OPTION_HEADER_ARRAY,
    RENDER_OPTION_DATA_AXIS,
    RENDER_OPTION_KEY_SEPERATOR, RENDER_OPTION_KEY_SKIP_EMPTY,
    RENDER_OPTION_MODE,
    RENDER_OPTION_INCLUDE_WINDOW_SPEC
] = [
    'roll_up', 'hierarchical', 'value_key', 'show_levels', 'iso_timestamp',
    'row_key', 'column_key', 'header_array', 'data_axis', 'key_separator', 'key_skip_empty',
    'mode', 'include_window_spec'
]
HEADER_ARRAY_OPTIONS = [HEADER_ARRAY_OPTION_ROW, HEADER_ARRAY_OPTION_COLUMN] = ['row', 'column']
DATA_AXIS_OPTIONS = [DATA_AXIS_ROW, DATA_AXIS_COLUMN] = ['row', 'column']

RENDER_MODE_NAMES = [
    RENDER_MODE_HEADER_ROW, RENDER_MODE_COMPACT, RENDER_MODE_SERIES, RENDER_MODE_HEADER_COLUMN,
    RENDER_MODE_FLAT_DICT, RENDER_MODE_HIER_DICT, RENDER_MODE_METRIC_FLAT_DICT,
    RENDER_MODE_DESC, RENDER_MODE_UPLOAD, RENDER_MODE_COMPACT_WS, RENDER_MODE_CSV
] = [
    'RENDER_MODE_HEADER_ROW', 'RENDER_MODE_COMPACT', 'RENDER_MODE_SERIES', 'RENDER_MODE_HEADER_COLUMN',
    'RENDER_MODE_FLAT_DICT', 'RENDER_MODE_HIER_DICT', 'RENDER_MODE_METRIC_FLAT_DICT',
    'RENDER_MODE_DESC', 'RENDER_MODE_UPLOAD', 'RENDER_MODE_COMPACT_WS', 'RENDER_MODE_CSV'
]

RENDER_OPTIONS = {
    RENDER_OPTION_ROLL_UP: {
        'description': 'move up attributes on rows (or columns) that are the same for \
            all rows (or columns) to a table attribute. \
            Levels enumerated in \'hierarchical\' are excluded.',
        'type': 'boolean'
    },
    RENDER_OPTION_HIERARCHICAL: {
        'description': 'if true, use hierarchical objects to represent multiple row (or column) dimensions, \
            otherwise multi-keys get concatenated with a dot-delimiter. If the value is \
            a list, only these levels are kept as separate levels, while remaining levels get concatenated keys',
        'type': 'array'
    },
    RENDER_OPTION_VALUE_KEY: {
        'description': 'if set, use this key in the value object to report data values',
        'type': 'string'
    },
    RENDER_OPTION_SHOW_LEVELS: {
        'description': 'if set, report the levels used in the data values (either hierarchical or flat)',
        'type': 'boolean'
    },
    RENDER_OPTION_ISO_TIMESTAMP: {
        'description': 'if set, render timestamps in a row or column index with both epoch and iso representations',
        'type': 'boolean'
    },
    RENDER_OPTION_ROW_KEY: {
        'description': 'if set, use this key as name of the row-dimension for single-dimensional rows',
        'type': 'string'
    },
    RENDER_OPTION_COLUMN_KEY: {
        'description': 'if set, use this key as name of the column-dimension for single-dimensional columns',
        'type': 'string'
    },
    RENDER_OPTION_HEADER_ARRAY: {
        'description': 'if set, report data as an header and an array.  ',
        'enum': HEADER_ARRAY_OPTIONS,
        'default': False
    },
    RENDER_OPTION_DATA_AXIS: {
        'description': 'orientation of the tabular data as a array of arrays',
        'enum': DATA_AXIS_OPTIONS
    },
    RENDER_OPTION_KEY_SEPERATOR: {
        'description': 'character used to concatenate multi-key columns or rows when required',
        'type': 'string',
        'default': '.'
    },
    RENDER_OPTION_KEY_SKIP_EMPTY: {
        'description': 'skip empty values in concatenating multi-key column or row headers',
        'type': 'boolean',
        'default': False
    },
    RENDER_OPTION_MODE: {
        'description': 'if set, use a preconfigured render mode with this name',
        'type': 'string',
        'enum': RENDER_MODE_NAMES
    },
    RENDER_OPTION_INCLUDE_WINDOW_SPEC: {
        'description': 'if set, include window specification in render modes that support it',
        'type': 'boolean'
    }
}

RENDER_MODES = {
    RENDER_MODE_HEADER_ROW: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HEADER_ARRAY: HEADER_ARRAY_OPTION_ROW,
            RENDER_OPTION_ROLL_UP: False,
            RENDER_OPTION_DATA_AXIS: DATA_AXIS_COLUMN
        }
    },
    RENDER_MODE_COMPACT: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: False,
            RENDER_OPTION_HEADER_ARRAY: HEADER_ARRAY_OPTION_ROW,
            RENDER_OPTION_ROLL_UP: False,
            RENDER_OPTION_DATA_AXIS: DATA_AXIS_COLUMN
        }
    },
    RENDER_MODE_COMPACT_WS: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: False,
            RENDER_OPTION_HEADER_ARRAY: HEADER_ARRAY_OPTION_ROW,
            RENDER_OPTION_ROLL_UP: False,
            RENDER_OPTION_DATA_AXIS: DATA_AXIS_COLUMN,
            RENDER_OPTION_INCLUDE_WINDOW_SPEC: True
        }
    },
    RENDER_MODE_SERIES: {
        "description": "report columns seperately and data as array by column",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: False,
            RENDER_OPTION_HEADER_ARRAY: HEADER_ARRAY_OPTION_ROW,
            RENDER_OPTION_DATA_AXIS: DATA_AXIS_ROW,
            RENDER_OPTION_ROLL_UP: True,
            RENDER_OPTION_INCLUDE_WINDOW_SPEC: True
        }
    },
    RENDER_MODE_HEADER_COLUMN: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HEADER_ARRAY: HEADER_ARRAY_OPTION_COLUMN,
            RENDER_OPTION_ROLL_UP: False,
            RENDER_OPTION_DATA_AXIS: DATA_AXIS_ROW
        },
    },
    RENDER_MODE_FLAT_DICT: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HIERARCHICAL: False,
            RENDER_OPTION_SHOW_LEVELS: True,
            RENDER_OPTION_ROLL_UP: False
        },
    },
    RENDER_MODE_HIER_DICT: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HIERARCHICAL: True,
            RENDER_OPTION_SHOW_LEVELS: True,
            RENDER_OPTION_ROLL_UP: True
        },
    },
    RENDER_MODE_METRIC_FLAT_DICT: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HIERARCHICAL: ['metric'],
            RENDER_OPTION_SHOW_LEVELS: False,
            RENDER_OPTION_ROLL_UP: True,
            RENDER_OPTION_KEY_SKIP_EMPTY: True
        },
    },
    RENDER_MODE_DESC: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: True,
            RENDER_OPTION_HIERARCHICAL: ['metric'],
            RENDER_OPTION_SHOW_LEVELS: True,
            RENDER_OPTION_ROLL_UP: True
        },
    },
    RENDER_MODE_UPLOAD: {
        "description": "",
        "options": {
            RENDER_OPTION_ISO_TIMESTAMP: False,
            RENDER_OPTION_HIERARCHICAL: False,
            RENDER_OPTION_SHOW_LEVELS: False,
            RENDER_OPTION_ROLL_UP: True
        },
    },
}


def get_column_names(data, cfg, sep='/'):
    """Retrieve columnn names for CSV rendering."""
    columns_order = ['resource', 'metric', 'aggregation', 'role']
    columns = []
    column_names = data.columns.names
    for i, column in enumerate(data.columns.values):
        name = cfg.data_options_list[i].get('name')
        if not name:
            # sort by column name using columns_order index
            column_dict = dict(zip(column_names, column))
            sorted_column = [column_dict[column] for column in columns_order if column_dict.get(column)]
            name = sep.join(sorted_column)
        columns.append(name)

    return columns


def df_to_csv(dataframe, cfg):
    """Render a dataframe to a CSV string."""
    dataframe = _prepare_data_frame(dataframe, hierarchical=['resource', 'metric'])
    columns = get_column_names(dataframe, cfg)
    # Use ISO formatting with microsecond support
    return dataframe.to_csv(header=columns, index_label='timestamp', date_format='%Y-%m-%dT%H:%M:%S.%fZ')


def df(pandas_object, render_mode=RENDER_MODE_METRIC_FLAT_DICT, render_options=None):
    """Render a dataframe to a json-serializable value."""
    if (render_options is not None and 'render_mode' in render_options):
        render_mode = render_options['render_mode']
    r_args = RENDER_MODES.get(render_mode, {}).get('options', {}).copy()
    if render_options:
        r_args.update(render_options)
    ha_opt = r_args.get(RENDER_OPTION_HEADER_ARRAY, False)
    if not ha_opt:
        raise NotImplementedError(f'Render in object format not supported')
    if ha_opt == HEADER_ARRAY_OPTION_COLUMN:
        return _df_header_column_array(pandas_object, **r_args)
    if ha_opt == HEADER_ARRAY_OPTION_ROW:
        return _df_header_row_array(pandas_object, **r_args)
    raise ValueError(f'Cannot render with option {RENDER_OPTION_HEADER_ARRAY}={ha_opt}')


def df1(pandas_object, render_mode=RENDER_MODE_METRIC_FLAT_DICT, render_options=None):
    """Render a dataframe to a json-serializable value."""
    r = df(pandas_object, render_mode, render_options)
    if isinstance(r, list):
        return r[0] if len(r) == 1 else {} if len(r) == 0 else r
    return r


def parse_df(data, render_mode=None, render_options=None):
    """Parse a json-compatible data structure to a Dataframe."""
    if render_mode is None:
        if isinstance(data, dict) and 'data' in data:
            if 'rows' in data:
                render_mode = RENDER_MODE_HEADER_COLUMN
            elif 'columns' in data:
                render_mode = RENDER_MODE_HEADER_ROW
        else:
            render_mode = RENDER_MODE_HIER_DICT
    r_args = RENDER_MODES.get(render_mode, {}).get('options', {}).copy()
    if render_options:
        r_args.update(render_options)
    ha = r_args.get(RENDER_OPTION_HEADER_ARRAY, False)
    if not ha:
        raise NotImplementedError(f'Render in object format not supported')
    if ha == HEADER_ARRAY_OPTION_COLUMN:
        return _parse_df_header_column_array(data, **r_args)
    if ha == HEADER_ARRAY_OPTION_ROW:
        return _parse_df_header_row_array(data, **r_args)
    raise ValueError(f'Cannot parse with option {RENDER_OPTION_HEADER_ARRAY}={ha}')


def _parse_df_header_column_array(data, data_axis=DATA_AXIS_ROW, **r_arg):
    if 'rows' not in data:
        raise ValueError('cannot parse row-based data without `rows` specification')
    raise NotImplementedError()


def _parse_df_header_row_array(data, data_axis=DATA_AXIS_COLUMN, **r_arg):

    data_values = data.get('data', [])

    if data_axis == DATA_AXIS_COLUMN:
        dataframe = pd.DataFrame(data_values)
    else:
        dataframe = pd.DataFrame()
        for col_idx, data_series in enumerate(data_values):
            dataframe[col_idx] = data_series

    if 'columns' in data:
        row_names, column_index = _parse_row_names_and_column_index(data['columns'])
        if len(dataframe) == 0:
            dataframe = pd.DataFrame(columns=column_index, index=pd.DatetimeIndex([], name='timestamp'))
        else:
            if row_names[0] == 'timestamp':
                idx = pd.DatetimeIndex(
                    pd.to_datetime(dataframe.iloc[:, 0], unit='ms', utc=True),
                    name='timestamp'
                )
                dataframe = dataframe.iloc[:, len(row_names):].set_index(idx)
                row_names = row_names[1:]
            elif row_names:
                dataframe = dataframe.set_index(list(range(len(row_names))))  # pylint: disable=no-member
                dataframe.index.names = row_names
            dataframe.columns = column_index

    if 'attributes' in data:
        dataframe.tsa.table_attributes.update(data['attributes'])
    return dataframe


def _parse_row_names_and_column_index(column_data):
    row_names = []
    column_names = OrderedDict()
    column_keys = []

    col_ordinal_mapping = {'resource': 0, 'metric': 1, 'aggregate': 2}

    def col_sorting_key(col_item):
        col_key = col_item[0]
        return (col_ordinal_mapping.get(col_key, len(col_ordinal_mapping)), col_key)

    for c in column_data:
        if isinstance(c, str):
            row_names.append(c)
        elif isinstance(c, dict):
            for k, v in sorted(c.items(), key=col_sorting_key):
                column_names[k] = True
    for c in column_data:
        if not isinstance(c, str):
            column_keys.append(tuple(c.get(n, None) for n in column_names.keys()))
    return row_names, pd.MultiIndex.from_tuples(column_keys, names=column_names)


def _keys_and_key_series(index, key, iso_timestamp, **render_options):
    keys = []
    # pylint: disable=function-redefined
    key_series = []
    if isinstance(index, pd.DatetimeIndex):
        key = index.name or 'timestamp'
        keys.append(key)
        ts_values = list(
            (index - pd.Timestamp('1970-01-01T00:00Z')) // pd.Timedelta('1ms')
        ) if len(index) else []
        key_series.append(ts_values)
        if iso_timestamp:
            keys.append(key+'_iso')
            iso_ts_values = list(index.strftime('%Y-%m-%dT%H:%M:%S,%f%z'))
            key_series.append(iso_ts_values)
    elif isinstance(index, pd.MultiIndex):
        for lvl_idx, lvl_name in enumerate(index.names):
            keys.append(lvl_name)
            key_series.append(list(index.levels[lvl_idx]))
    elif isinstance(index, pd.RangeIndex):
        pass
    else:
        keys = [index.name or key]
        key_series.append([
            _render_value(v, **render_options) for v in index
        ])
    return keys, key_series


def _keys_and_key_renderer(index, key, iso_timestamp, **render_options):
    keys = None
    # pylint: disable=function-redefined
    key_renderer = None
    if isinstance(index, pd.DatetimeIndex):
        key = index.name or 'timestamp'
        if iso_timestamp:
            keys = [key, key+'_iso']

            def key_renderer(ts):
                return [int(ts.timestamp() * 1000), ts.isoformat()]
        else:
            keys = [key]

            def key_renderer(ts):
                return [int(ts.timestamp() * 1000)]
    elif isinstance(index, pd.MultiIndex):
        keys = list(index.names)

        def key_renderer(idx):
            return list(idx)
    elif isinstance(index, pd.RangeIndex):
        keys = []

        def key_renderer(idx):
            return []
    else:
        keys = [index.name or key]

        def key_renderer(idx):
            return [_render_value(idx, **render_options)]
    return keys, key_renderer


def _header_renderer(index, key, iso_timestamp):
    # pylint: disable=function-redefined
    header_renderer = None
    if isinstance(index, pd.DatetimeIndex):
        key = index.name or 'timestamp'
        if iso_timestamp:
            def header_renderer(ts):
                return {key: int(round(ts.timestamp() * 1000)), key+'_iso': ts.isoformat()}
        else:
            def header_renderer(ts):
                return {key: int(round(ts.timestamp() * 1000))}
    elif isinstance(index, pd.MultiIndex):
        def header_renderer(col):
            return {index.names[i]: _render_value(v) for i, v in enumerate(col) if v is not None and v != ''}
    elif key or index.name:
        key = index.name or key

        def header_renderer(col):
            return {key: _render_value(col)}
    elif isinstance(index, pd.RangeIndex):
        header_renderer = _render_value
    else:
        header_renderer = _render_value
    return header_renderer


def _df_header_row_array(
        pandas_object, row_key='row',
        column_key=None, iso_timestamp=True, data_axis=DATA_AXIS_COLUMN,
        **render_options
):
    if pandas_object is None:
        pandas_object = pd.DataFrame()
    data_frame = _prepare_data_frame(pandas_object, **render_options)
    column_renderer = _header_renderer(data_frame.columns, column_key, iso_timestamp)
    if data_axis == DATA_AXIS_COLUMN:
        row_keys, row_key_renderer = _keys_and_key_renderer(data_frame.index, row_key, iso_timestamp)
        data = [
            row_key_renderer(k) + [_render_value(v, **render_options) for v in r.values]
            for k, r in data_frame.iterrows()
        ]
    else:
        row_keys, index_series = _keys_and_key_series(data_frame.index, row_key, iso_timestamp)
        data = index_series + [
            [_render_value(v, **render_options) for v in data_frame[col]]
            for col in data_frame.columns
        ]
    columns = (row_keys + [column_renderer(col) for col in data_frame.columns])
    return _add_attributes_and_window_spec(data_frame, OrderedDict(
        columns=columns,
        data=data,
        data_axis=data_axis
    ), **render_options)


def _add_attributes_and_window_spec(data_frame, result, include_window_spec=False, **render_options):
    attributes = data_frame.tsa.table_attributes
    if attributes:
        result['attributes'] = _render_dict(attributes, **render_options)
    if include_window_spec:
        window_spec = data_frame.tsa.window_spec
        if window_spec:
            result['window_spec'] = _render_dict(window_spec, **render_options)
    return result


def _df_header_column_array(
        pandas_object, row_key=None,
        column_key='column', iso_timestamp=True,  data_axis=DATA_AXIS_ROW,
        **render_options
):
    if pandas_object is None:
        pandas_object = pd.DataFrame()
    data_frame = _prepare_data_frame(pandas_object, **render_options)
    row_renderer = _header_renderer(data_frame.index, row_key, iso_timestamp)
    if data_axis == DATA_AXIS_ROW:
        column_keys, column_key_renderer = _keys_and_key_renderer(data_frame.columns, column_key, iso_timestamp)
        data = [
            column_key_renderer(col) + [_render_value(v, **render_options) for v in data_frame[col].values]
            for col in data_frame.columns
        ]
    else:
        column_keys, columns_series = _keys_and_key_series(data_frame.columns, column_key, iso_timestamp)
        data = columns_series + [
            [_render_value(v, **render_options) for v in row_series]
            for idx, row_series in data_frame.iterrows()
        ]
    return _add_attributes_and_window_spec(data_frame, OrderedDict(
        rows=(column_keys + [row_renderer(idx) for idx in data_frame.index]),
        data=data,
        data_axis=data_axis,
    ), **render_options)


def _roll_up_single_level_columns(data_frame, keep_hashed, value_key):
    return _roll_up_single_level(data_frame, 1, keep_hashed, value_key)


def _roll_up_single_level_rows(data_frame, keep_hashed, value_key):
    return _roll_up_single_level(data_frame, 0, keep_hashed, value_key)


def _roll_up_single_level(data_frame, axis, keep_hashed, value_key):
    table_attributes = data_frame.tsa.table_attributes.copy()
    index = data_frame.axes[axis]
    hashed = [name for name in index.names if name in keep_hashed]
    current_level = 0
    while isinstance(index, pd.MultiIndex) and len(index.names) > len(hashed):
        level_name = index.names[current_level]
        labels = set(index.get_level_values(current_level))
        non_empty_labels = [la for la in labels if la != '']
        if level_name in hashed:
            current_level += 1
        elif len(non_empty_labels) == 1:
            # other column dimensions (resource, aggregation, ... )
            # are rolled up if they have only one value (not counting empty labels)
            label = non_empty_labels[0]
            table_attributes[level_name] = label
            rolled_up_data_frame = data_frame.xs(label, axis=axis, level=current_level)
            if len(labels) == 2:
                data_frame = rolled_up_data_frame.join(data_frame.xs(
                    '', axis=axis, level=current_level), lsuffix='_default')
            else:
                data_frame = rolled_up_data_frame
            index = data_frame.axes[axis]
        else:
            hashed = hashed + [level_name]
            current_level += 1
    if len(index.names) == 1 and len(index) == 1 and index.name and index.name not in hashed and value_key:
        table_attributes[index.name] = index[0]
        data_frame = data_frame.set_axis(pd.Index([value_key]), axis=axis, inplace=False)

    data_frame.tsa.table_attributes.update(table_attributes)
    return data_frame


def _prepare_data_frame(
        pandas_object, roll_up=True,
        hierarchical=['metric'], value_key='value', **kwargs
):
    if isinstance(pandas_object, pd.Series):
        if isinstance(pandas_object.index, (pd.DatetimeIndex, pd.RangeIndex)):
            data_frame = pandas_object.to_frame()
        else:
            data_frame = pandas_object.to_frame().T
        if len(data_frame.columns) > 1:
            data_frame.columns.names = ["col"+str(i) for i in range(0, len(data_frame.columns.names))]
    elif isinstance(pandas_object, pd.DataFrame):
        data_frame = pandas_object
    else:
        raise ValueError('not a pandas object: {}'.format(pandas_object))
    if roll_up:
        keep_hashed = hierarchical if isinstance(hierarchical, list) else []
        data_frame = _roll_up_single_level_columns(data_frame, keep_hashed, value_key)
        data_frame = _roll_up_single_level_rows(data_frame, keep_hashed, value_key)
    return data_frame


def _render_multi_index_row_to_dict(row):
    if len(row.index.names) > 1:
        row_dict = {}
        for sub_key, sub_row in row.groupby(level=0):
            if sub_key != '':
                row_dict[sub_key] = _render_multi_index_row_to_dict(sub_row.xs(sub_key))
            else:
                # empty keys get render on level above .. ???
                row_dict.update(_render_multi_index_row_to_dict(sub_row.xs(sub_key)))
        return row_dict
    return row.to_dict()


def _render_key(k, key_separator='.', key_skip_empty=False, **kwargs):
    if isinstance(k, str):
        return k
    if isinstance(k, Iterable):
        if key_skip_empty:
            return key_separator.join([str(v) for v in k if v != ''])
        return key_separator.join([str(v) for v in k])
    return str(k)


def render(value, **render_options):
    """Convert a value to a json-serializable one."""
    return _render_value(value, **render_options)


def render_timestamp(value, iso_timestamp=False, **render_options):
    """Render a timestamp."""
    if iso_timestamp:
        return value.isoformat()
    return int(value.timestamp() * 1000)


def _render_value(v, **render_options):
    if isinstance(v, str):
        return v
    if isinstance(v, pd.Timestamp):
        return render_timestamp(v, **render_options)
    if isinstance(v, datetime.datetime):
        return render_timestamp(v, True, **render_options)
    if isinstance(v, pd.Timedelta):
        return tsa_to_iso_freq(v)
    if isinstance(v, np.generic):
        if np.isfinite(v):
            return v.item()
        return None
    if isinstance(v, float):
        if np.isfinite(v):
            return v
        return None
    if isinstance(v, list):
        return [_render_value(item, **render_options) for item in v]
    if isinstance(v, dict):
        return _render_dict(v, **render_options)
    if isinstance(v, np.ndarray):
        return [_render_value(item, **render_options) for item in v]
    if hasattr(v, 'render'):
        return v.render()
    if dataclasses.is_dataclass(v):
        return OrderedDict([
            (f.name, _render_value(getattr(v, f.name), **render_options))
            for f in dataclasses.fields(v)
        ])
    if isinstance(v, PandasObject):
        return df1(v, render_options=render_options)
    if pd.isnull(v):
        return None
    return v


def _render_dict(dict_like, **render_options):
    if len(dict_like) == 1 and '' in dict_like:
        return _render_value(dict_like[''], **render_options)

    return OrderedDict([
        (_render_key(key, **render_options), _render_value(val, **render_options)) for key, val in dict_like.items()
    ])
