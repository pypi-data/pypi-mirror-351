"""Reader utilities for a etl-formatted file."""
from typing import (
    Iterator, Sequence, List,
    Union, Optional, Callable,
    Tuple, Any
)

from datetime import datetime
import csv
import gzip
from contextlib import contextmanager

import pandas as pd

from .model import (
    WaylayETLSeriesImport,
    SeriesIterator,
    MeasurementValue,
    MeasurementIterator,
    Resource,
    Metric,
    SeriesSettings,
    CSVReader,
    METRIC_PREFIX,
    METRIC_PREFIX_LENGTH,
    RESOURCE_IDX, METRIC_IDX, TIMESTAMP_IDX, VALUE_IDX,
    RESOURCE_COLUMN, METRIC_COLUMN, TIMESTAMP_COLUMN,
    ParserRequestError,
    try_parse_float,
    parse_timestamp,
)


@contextmanager
def read_etl_import_as_stream(etl_import: WaylayETLSeriesImport) -> Iterator[CSVReader]:
    """Iterate of the content of stored etl file (gzipped csv file)."""
    path = etl_import.import_file.path
    if not path.exists():
        raise ParserRequestError(
            f'Cannot read from etl import file {path}: does not exist.'
        )
    with gzip.open(path, 'rt') as csv_file:
        yield csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)


@contextmanager
def read_etl_import(etl_import: WaylayETLSeriesImport) -> Iterator[SeriesIterator]:
    """Create a Series Iterator from a stored etl file (gzipped csv file)."""
    path = etl_import.import_file.path
    if not path.exists():
        raise ParserRequestError(
            f'Cannot read from etl import file {path}: does not exist.'
        )
    with gzip.open(path, 'rt') as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        yield SeriesCursor(reader, list(etl_import.settings.iter_metrics())).iter_series()


def dataframe_from_iterator(series_iterator: SeriesIterator) -> pd.DataFrame:
    """Create a Pandas dataframe from a SeriesIterator."""
    resource_metric_dfs = list(
        pd.DataFrame(
            list(measurements),
            columns=[TIMESTAMP_COLUMN, (resource, metric)]
        ).set_index(TIMESTAMP_COLUMN)
        for resource, metric, measurements in series_iterator
    )
    resource_metric_df = pd.concat(resource_metric_dfs, axis=1)
    resource_metric_df.columns = pd.MultiIndex.from_tuples(
        resource_metric_df.columns,
        names=[RESOURCE_COLUMN, METRIC_COLUMN]
    )
    return resource_metric_df


def list_resources(settings: SeriesSettings, series_iterator: SeriesIterator) -> List[Resource]:
    """Get a `Resource` list that describes the resources an metrics found in the given series collection.

    Uses the `settings.resources` and `settings.metrics` as a data dictionary to enhance the
    _resource_ and _metric_ descriptions found in the series.
    """
    class ResourceDict(dict):
        def __missing__(self, key):
            self[key] = value = settings.resource_for(key, [])
            return value

    resource_dict = ResourceDict()
    for resource, metric, _ in series_iterator:
        resource_dict[resource].metrics.append(settings.metric_for(metric))

    return list(resource_dict.values())


DONE = False
NEXT = True

RESOURCE_IDX, METRIC_IDX, TIMESTAMP_IDX, VALUE_IDX = range(4)
SeriesRow = Tuple[Any]


class SeriesCursor:
    """A look-ahead polling cursor on a etl-formatted csv stream, splitting the series."""

    def __init__(
        self, reader,
        metrics: Optional[Sequence[Metric]] = None,
        on_close: Optional[Callable] = None
    ):
        """Create a Series reader.

        The reader should provide an iterator of string-formatted
        (timestamp, resource, metric, value) tuples.
        """
        self.reader = reader
        self._current_row: Union[None, bool, SeriesRow] = None
        self._next_row: Union[None, bool, SeriesRow] = None
        self._on_close: Optional[Callable] = on_close
        self._metrics: Optional[Sequence[Metric]] = metrics
        self._value_parser: Callable[[str], MeasurementValue] = try_parse_float
        self._metric_prefix_len = 0

    def _current_value_parser(self) -> Callable:
        # look up the value parser for the metric at the current cursor position.
        metric = self.metric
        if self._metrics:
            for metric_spec in self._metrics:
                if metric_spec.name == metric:
                    return metric_spec.get_value_parser()
        return try_parse_float

    def iter_rows(self) -> MeasurementIterator:
        """Get an iterator of the series at the current cursor position.

        Precondition:
        - a previous call to `next_series` should have returned `True`.
        """
        while self.next_row():
            yield self.timestamp, self.value

    def iter_series(self) -> SeriesIterator:
        """Get an iterator over (_metric_, _resource_, _series_) tuples.

        Warning:
            Each _series_ iterator returned in the tuple
            should first be depleted before handling the next record of this iterator.
            Out of order requests will lead to lost rows.
        """
        while self.next_series():
            yield self.resource, self.metric, self.iter_rows()  # type: ignore

    def next_series(self) -> bool:
        """Move the cursor to the next series.

        If this returns `False`, the cursor is at the end of the input.
        If this returns `True`, the `resource` and `metric` properties can be requested,
        and the available series can be iterated with `next_series`.
        """
        if self._current_row == NEXT:
            # consume all rows for this series
            while self.next_row():
                pass

        self._current_row = NEXT

        if self._next_row is None:
            # read first row
            self._next_row = next(self.reader, DONE)

        if self._next_row != DONE and self._next_row[TIMESTAMP_IDX] == TIMESTAMP_COLUMN:  # type: ignore
            # consume header row
            self._next_row = next(self.reader, DONE)

        if self._next_row == DONE:
            # last entry
            if self._on_close:
                self._on_close()
            return False

        # setup specific parser rules for this series.
        self._value_parser = self._current_value_parser()

        # inspect the prefixes of metrics, set up to ignore METRIC_PREFIX
        has_metric_prefix = METRIC_PREFIX in self._next_row[METRIC_IDX]  # type: ignore
        self._metric_prefix_len = METRIC_PREFIX_LENGTH if has_metric_prefix else 0

        return True

    def next_row(self) -> bool:
        """Move the cursor to the next row.

        Only if this returns `true`, the `value` and `timestamp` properties can be requested.
        If it returns `false`, a call to `next_series` should be issued to check completion.

        Precondition:
        - a previous call to `next_series` should have returned `True`.
        """
        if self._next_row is None:
            raise AssertionError('Illegal state: call `next_series` first!')

        if self._next_row == DONE:
            # last entry
            return False

        if self._current_row != NEXT and (
            self._next_row[RESOURCE_IDX] != self._current_row[RESOURCE_IDX] or  # type: ignore
            self._next_row[METRIC_IDX] != self._current_row[METRIC_IDX]    # type: ignore
        ):
            # new series (resource/metric changed)
            return False

        # read next row
        self._current_row = self._next_row
        self._next_row = next(self.reader, DONE)
        return True

    @property
    def resource(self) -> Optional[str]:
        """Get the _resource_ for the current cursor position.

        Precondition:
        - a previous call to `next_series` should have returned `True`.
        """
        return self._current_or_next(RESOURCE_IDX)

    @property
    def metric(self) -> Optional[str]:
        """Get the _metric_ for the current cursor position.

        Precondition:
        - a previous call to `next_series` should have returned `True`.
        """
        _metric = self._current_or_next(METRIC_IDX)
        return _metric[self._metric_prefix_len:]

    @property
    def timestamp(self) -> datetime:
        """Get the _timestamp_ for the current cursor position.

        Precondition:
        - a previous call to `next_row` should have returned `True`.
        """
        return parse_timestamp(self._current_row[TIMESTAMP_IDX])  # type: ignore

    @property
    def value(self) -> MeasurementValue:
        """Get the _value_ for the current cursor position.

        Precondition:
        - a previous call to `next_row` should have returned `True`.
        """
        return self._value_parser(self._current_row[VALUE_IDX])  # type: ignore

    def _current_or_next(self, idx):
        if self._current_row == NEXT:
            return self._next_row[idx]
        return self._current_row[idx]
