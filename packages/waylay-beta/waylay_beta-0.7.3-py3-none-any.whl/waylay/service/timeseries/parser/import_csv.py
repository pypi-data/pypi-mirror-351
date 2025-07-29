"""Conversion from CSV to elt export format."""

from collections import defaultdict
from enum import Enum
from typing import (
    Union, Dict, Sequence, Iterator, Iterable,
    Optional, Tuple, List, TextIO,
    cast,
)
from dataclasses import replace
import collections.abc
import os
import io
import csv
import gzip
import itertools
import tarfile
import pathlib
import logging
from contextlib import contextmanager
from datetime import datetime
from tarfile import TarFile
from zipfile import ZipFile

from tqdm import tqdm
import pandas as pd
from .model import (
    ArchiveType,
    SeriesInput,
    SeriesSettings,
    Measurement,
    MeasurementIterator,
    Metric,
    CSVReader,
    CSVReaderAndResource,
    PathLike,
    ETLFile,
    ETL_IMPORT_COLUMN_NAMES,
    RESOURCE_COLUMN,
    METRIC_COLUMN,
    VALUE_COLUMN,
    ParserRequestError,
    TIMESTAMP_COLUMN_NAMES,
)

from .util import (
    WrappeableSpooledTemporaryFile,
)

LOG = logging.getLogger(__name__)
TIMESERIES_SUFFIXES = ['timeseries.csv.gz', '-timeseries.csv']
DEFAULT_SPOOL_MAX_SIZE = 2 << 18

_SPOOLED_TS_LEN = 13
_SPOOLED_TS_FORMAT = '%013d'


class MeasurementsStoreType(Enum):
    """Enum for measurements store types."""

    MEMORY = 'memory'
    SPOOLED = 'spooled'


class CsvImportSeriesProvider(collections.abc.Mapping):
    """A series provider that uses cached buffers to process import csv files."""

    def __init__(
        self,
        settings: SeriesSettings,
        measurements_store: Union[str, MeasurementsStoreType] = MeasurementsStoreType.SPOOLED
    ):
        """Create an import series provider."""
        self.settings = settings
        if isinstance(measurements_store, MeasurementsStoreType):
            self._measurements_store = measurements_store.value
        elif measurements_store in [mt.value for mt in MeasurementsStoreType]:
            self._measurements_store = measurements_store
        else:
            logging.warning(
                "Series are sorted using limited memory buffers with overflow to file. "
                "This might use up the open file quota when importing many different series. "
                "Use measurements_store='memory' for a pure in-memory based solution. "
                "Use measurements_store='spooled' to suppress this warning"
            )
            self._measurements_store = MeasurementsStoreType.SPOOLED.value
        self._measurements: Dict[Tuple[str, str], Union[TextIO, io.StringIO]] = defaultdict(self._new_buffer)
        self._reading = False
        self._written = 0
        self.row_count = 0
        self.input_count = 0
        self.spool_size_left = DEFAULT_SPOOL_MAX_SIZE

    def _new_buffer(self) -> Union[TextIO, io.StringIO]:
        if self._measurements_store == MeasurementsStoreType.MEMORY.value:
            return io.StringIO()
        else:
            max_size = int(self.spool_size_left / 2)
            self.spool_size_left -= max_size
            return io.TextIOWrapper(WrappeableSpooledTemporaryFile(max_size=max_size, mode='w+b'))

    def __enter__(self):
        """Enter a runtime context."""
        assert not self._reading
        return self

    def __exit__(self, exc, value, tb):
        """Leave a runtime context, cleaning up all buffers."""
        self.close()

    def close(self):
        """Close all buffers."""
        for buffer in self._measurements.values():
            buffer.close()

    def __iter__(self):
        """Iterate over the (resource, metric) keys of this provider."""
        return iter(self._measurements)

    def __len__(self):
        """Get the number of requested (resource,metric) combinations."""
        return len(self._measurements)

    def __getitem__(self, resource_metric: Tuple[str, str]) -> Iterable[Measurement]:
        """Create an measurement iterable for a given resource, metric."""
        resource, metric = resource_metric
        provider = self

        class _MeasurementIterable():
            def __iter__(self) -> Iterator[Measurement]:
                return provider._iter_single_series_export(resource, metric)

        return _MeasurementIterable()

    @staticmethod
    def _write_measurement_to_buffer(target: Union[io.StringIO, TextIO], timestamp: datetime, value):
        target.write(_SPOOLED_TS_FORMAT % int(timestamp.timestamp() * 1000))
        target.write(str(value))
        target.write('\n')

    @staticmethod
    def _peek_reader(csv_data: CSVReader) -> Tuple[Sequence[str], Optional[Sequence[str]], CSVReader]:
        header = next(csv_data)
        first_data_line: Optional[Sequence[str]] = []
        while first_data_line == []:
            first_data_line = next(csv_data, None)

        # restore the iterator from which we read the first line
        if first_data_line:
            csv_data = itertools.chain([first_data_line], csv_data)
        return header, first_data_line, csv_data

    def _prepare_settings(
        self, header: Sequence[str],
        example_data: Sequence[str],
        default_resource_id: Optional[str]
    ) -> SeriesSettings:
        settings = _prepare_csvheader_timestamp(self.settings, header, example_data)

        if default_resource_id and settings.resource is None:
            settings = replace(settings, resource=default_resource_id)
        settings = _prepare_csvheader_resource_metric(header, settings)
        if settings.value_column or all(column in header for column in ETL_IMPORT_COLUMN_NAMES):
            # single column contains values, metric must be provided fixed or as other column.
            settings = _prepare_csvheader_value_column(header, settings)
        else:
            # series specified in seperate columns
            settings = _prepare_csvheader_series_column(header, settings)
        return settings

    @staticmethod
    def _header_indices(
        header: Sequence[str],
        settings: SeriesSettings
    ):
        timestamp_idx = header.index(settings.timestamp_column)
        resource_idx = None
        metric_idx = None
        value_idx = None
        if settings.resource_column is not None:
            resource_idx = header.index(settings.resource_column)
        if settings.metric_column is not None:
            metric_idx = header.index(settings.metric_column)
        if settings.value_column is not None:
            value_idx = header.index(settings.value_column)

        return resource_idx, metric_idx, timestamp_idx, value_idx

    def add_csv_data(self, csv_data: CSVReader, default_resource_id: Optional[str]) -> int:
        """Add a csv data to the measurement buffer."""
        if self._reading:
            raise RuntimeError('Cannot write to import buffer after reading from it.')

        self.input_count += 1

        header, first_data_line, csv_data = self._peek_reader(csv_data)
        if first_data_line is None:
            # empty csv file
            return 0

        settings = self._prepare_settings(header, first_data_line, default_resource_id)

        create_timestamp = settings.get_timestamp_parser()
        assert create_timestamp

        resource_idx, metric_idx, timestamp_idx, value_idx = self._header_indices(header, settings)

        if value_idx is not None:
            # normalised, single-value csv
            def _handle_csv_normalized(item):
                resource_id = settings.resource_by_key(item[resource_idx] if resource_idx is not None else None)
                metric_name = settings.metric_by_key(item[metric_idx] if metric_idx is not None else None)
                if resource_id and metric_name:
                    self._write_measurement_to_buffer(
                        self._measurements[(resource_id, metric_name)],
                        create_timestamp(item[timestamp_idx]),
                        item[value_idx]
                    )
                    return 1
                return 0

            item_handler = _handle_csv_normalized
        elif resource_idx is not None:
            # value in columns with metric key, with resource column
            value_idx_and_metric_name: List[Tuple[int, str]] = []
            for value_idx, metric_key in enumerate(header):
                if value_idx in (resource_idx, timestamp_idx):
                    continue
                metric_name = settings.metric_by_key(metric_key)
                if metric_name is not None:
                    value_idx_and_metric_name.append((value_idx, metric_name))
            value_count = len(value_idx_and_metric_name)

            def _handle_csv_with_resource(item):
                resource_id = settings.resource_by_key(item[resource_idx])
                if resource_id is None:
                    return 0
                for value_idx, metric_name in value_idx_and_metric_name:
                    self._write_measurement_to_buffer(
                        self._measurements[(resource_id, metric_name)],
                        create_timestamp(item[timestamp_idx]),
                        item[value_idx]
                    )
                return value_count

            item_handler = _handle_csv_with_resource
        else:
            # value in columns with metric key, no resource column
            resource_id = settings.resource
            if resource_id is None:
                raise ParserRequestError('No default resource id provided.')

            value_idx_and_measurements: List[Tuple[int, TextIO]] = []
            for value_idx, metric_key in enumerate(header):
                if value_idx in (resource_idx, timestamp_idx):
                    continue
                metric_name = settings.metric_by_key(metric_key)
                if metric_name:
                    measurements = self._measurements[(resource_id, metric_name)]
                    value_idx_and_measurements.append((value_idx, measurements))
            value_count = len(value_idx_and_measurements)

            def _handle_csv_without_resource(item):
                for value_idx, measurements in value_idx_and_measurements:
                    self._write_measurement_to_buffer(
                        measurements,
                        create_timestamp(item[timestamp_idx]),
                        item[value_idx]
                    )
                return value_count
            item_handler = _handle_csv_without_resource

        row_count = 0
        for item in csv_data:
            # skip empty lines
            if item:
                row_count += item_handler(item)
        self.row_count += row_count
        return row_count

    def flip(self):
        """Switch from writing to reading mode."""
        if self._reading:
            return
        self._reading = True
        for buffer in self._measurements.values():
            self._written += buffer.tell()
            buffer.seek(0)

    def _iter_single_series_export(
        self,
        resource_id: str, metric_name: str
    ) -> MeasurementIterator:
        """Paging iterator over the specified resource and metric."""
        self.flip()
        measure_buffer = self._measurements[(resource_id, metric_name)]
        measure_buffer.seek(0)
        for line in measure_buffer:
            yield (
                pd.Timestamp(int(line[:_SPOOLED_TS_LEN]), unit='ms', tz='UTC'),
                # do not read \n
                line[_SPOOLED_TS_LEN:-1]
            )


def prepare_settings_csv(
    *input_data: SeriesInput,
    settings: SeriesSettings,
) -> SeriesSettings:
    """Validate and update the input settings by extracting metadata from a csv header."""
    original_settings = settings
    input_count = 0
    for csv_data, default_resource_id in open_csv(*input_data):
        input_count += 1
        header = next(csv_data)
        example = next(csv_data, None)
        settings = original_settings
        if not settings.resource:
            settings = replace(settings, resource=default_resource_id)

        settings = _prepare_csvheader_timestamp(settings, header, example)

        settings = _prepare_csvheader_resource_metric(header, settings)

        if settings.value_column or all(column in header for column in ETL_IMPORT_COLUMN_NAMES):
            # single column contains values, metric must be provided fixed or as other column.
            settings = _prepare_csvheader_value_column(header, settings)
        else:
            # series specified in seperate columns
            settings = _prepare_csvheader_series_column(header, settings)

    if input_count == 0:
        raise ParserRequestError('No input data')
    if input_count == 1:
        return settings
    return original_settings


def _prepare_csvheader_timestamp(
    settings: SeriesSettings, header: Sequence[str], example: Optional[Sequence[str]]
) -> SeriesSettings:
    # time column handling
    if settings.timestamp_column:
        if settings.timestamp_column not in header:
            raise ParserRequestError(
                f'Timestamp column `{settings.timestamp_column}` not in csv header {header}.'
            )
    elif settings.timestamp_first and settings.timestamp_interval:
        raise NotImplementedError('timestamp_first timestamp_interval setting not supported')
    else:
        for timestamp_column in TIMESTAMP_COLUMN_NAMES:
            if timestamp_column in header:
                settings = replace(settings, timestamp_column=timestamp_column)
                break
        if not settings.timestamp_column:
            raise ParserRequestError(
                f'No timestamp column found in `{header}`'
            )

    # default timestamp value constructor
    if settings.timestamp_column:
        timestamp_idx = next(
            idx for idx, col in enumerate(header)
            if col == settings.timestamp_column
        )
        example_timestamp = example[timestamp_idx] if example else None
        timestamp_constructor = settings.get_timestamp_parser(example_timestamp)
        if settings.timestamp_offset:
            offset = settings.timestamp_offset
            original_timestamp_constructor = timestamp_constructor

            def timestamp_constructor_offset(ts):
                return original_timestamp_constructor(ts) + offset

            timestamp_constructor = timestamp_constructor_offset

        settings = replace(
            settings,
            timestamp_constructor=timestamp_constructor
        )
    return settings


def _prepare_csvheader_resource_metric(header: Sequence[str], settings: SeriesSettings) -> SeriesSettings:
    if not settings.resource_column:
        if RESOURCE_COLUMN in header:
            settings = replace(settings, resource_column=RESOURCE_COLUMN)
        elif settings.resource is None:
            raise ParserRequestError(
                f'No valid resource column or default provided: `{settings.resource_column}`'
            )
    if settings.resource_column:
        if settings.resource_column not in header:
            raise ParserRequestError(
                f'Invalid resource column provided: `{settings.resource_column}`'
            )
    if settings.metric_column:
        if settings.metric_column not in header:
            raise ParserRequestError(
                f'Invalid metric column provided: `{settings.metric_column}`'
            )
    return settings


def _prepare_csvheader_value_column(header: Sequence[str], settings: SeriesSettings) -> SeriesSettings:
    if not settings.value_column:
        settings = replace(settings, value_column=VALUE_COLUMN)
    if settings.value_column not in header:
        raise ParserRequestError(
            f'Value column `{settings.value_column}` not in csv header {header}.'
        )
    if settings.metric_column is None:
        if METRIC_COLUMN in header:
            settings = replace(settings, metric_column=METRIC_COLUMN)
        elif settings.metric is None:
            raise ParserRequestError(
                f'No valid metric column or default provided for values in `{settings.value_column}` column.'
            )
    return settings


def _prepare_csvheader_series_column(header: Sequence[str], settings: SeriesSettings) -> SeriesSettings:
    specified_metrics = list(settings.iter_metrics())
    if not specified_metrics:
        specified_metrics = [
            Metric(name=column)
            for column in header
            if column != settings.timestamp_column
            if column != settings.resource_column
        ]

    specified_metrics = [
        metric_spec
        for metric_spec in specified_metrics
        if metric_spec.key_or_name in header
    ]
    if not specified_metrics:
        raise ParserRequestError(
            f'None of the specified metrics `{settings.metrics}` found in the csv header.'
        )
    return replace(settings, metrics=specified_metrics)


@contextmanager
def create_import_series_provider(
    *series_input: SeriesInput,
    settings: SeriesSettings,
    progress: bool = False,
    measurements_store: MeasurementsStoreType = MeasurementsStoreType.SPOOLED
) -> Iterator[CsvImportSeriesProvider]:
    """Create a SeriesProvider from the given csv input and settings.

    This reads the csv input into buffers, ready to export to an etl file.
    Returns a context manager, that closes all temporary buffers on leaving the context.
    """
    with CsvImportSeriesProvider(settings, measurements_store) as series_provider:
        if progress:
            with tqdm(
                total=series_provider.input_count, unit='csv_files', unit_scale=True, unit_divisor=1
            ) as progress_tqdm:
                for csv_reader, default_resource_id in open_csv(*series_input):
                    series_provider.add_csv_data(csv_reader, default_resource_id)
                    progress_tqdm.update()
        else:
            for csv_reader, default_resource_id in open_csv(*series_input):
                series_provider.add_csv_data(csv_reader, default_resource_id)

        yield series_provider


def open_csv(*series_inputs: SeriesInput, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    """Open the CSV file specified by this input."""
    for series_input in series_inputs:
        yield from _open_csv(series_input, **csv_format_args)


def _open_csv(series_input: SeriesInput, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    if isinstance(series_input, ETLFile):
        LOG.debug('reading csv from %s', series_input.path)
        yield from _open_csv_gz_file(series_input.path, **csv_format_args)
    elif isinstance(series_input, (str, os.PathLike)):
        series_path = pathlib.Path(series_input)
        archive_type = ArchiveType.for_import(series_path)
        LOG.debug('reading from %s as %s', series_path, archive_type)

        if archive_type == ArchiveType.GZ:
            yield from _open_csv_gz_file(series_path, **csv_format_args)
        elif archive_type == ArchiveType.ZIP:
            yield from _open_csv_from_zip(series_path, **csv_format_args)
        elif archive_type in (ArchiveType.TAR, ArchiveType.TAR_GZ):
            yield from _open_csv_from_tar(series_path, **csv_format_args)
        elif archive_type == ArchiveType.TEXT:
            yield from _open_csv_file(series_path, **csv_format_args)
        elif archive_type == ArchiveType.DIR:
            for child_path in series_path.iterdir():
                yield from _open_csv(child_path, **csv_format_args)
        else:
            raise Exception(f'Unsupported input file {series_path} of type {archive_type}')

    elif isinstance(series_input, io.TextIOBase):
        LOG.debug('reading from text stream')
        yield from _reset_and_open_csv_text_stream(series_input, **csv_format_args)

    elif isinstance(series_input, Iterable):
        LOG.debug('reading from iterable')
        yield from _open_csv_iterable(series_input, **csv_format_args)

    else:
        raise Exception(f'Unsupported input type {type(series_input)}.')


def _open_csv_gz_file(series_input: PathLike, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with gzip.open(series_input, 'rt') as csv_file:
        yield csv.reader(cast(io.TextIOBase, csv_file), **csv_format_args), pathlib.Path(series_input).stem


def _open_csv_file(series_input: PathLike, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with open(series_input, 'rt') as csv_file:
        yield csv.reader(csv_file, **csv_format_args), pathlib.Path(series_input).stem


def _reset_and_open_csv_text_stream(series_input: io.TextIOBase, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    series_input.seek(0)
    yield csv.reader(series_input, **csv_format_args), None


def _open_csv_from_tar(series_input: pathlib.Path, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with tarfile.open(series_input, 'r') as tar_archive:
        for entry_name in tar_archive.getnames():
            LOG.debug('reading tar entry %s from %s', entry_name, series_input)
            if any(entry_name.endswith(suffix) for suffix in TIMESERIES_SUFFIXES):
                yield from _open_csv_gz_from_tar_entry(tar_archive, entry_name, **csv_format_args)
            else:
                yield from _open_csv_from_tar_entry(tar_archive, entry_name, **csv_format_args)


def _open_csv_from_tar_entry(archive: TarFile, entry: str, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    csv_file = archive.extractfile(entry)
    if csv_file:
        yield csv.reader(io.TextIOWrapper(csv_file), **csv_format_args), pathlib.Path(entry).stem


def _open_csv_gz_from_tar_entry(archive: TarFile, entry: str, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    csv_gz_file = archive.extractfile(entry)
    if csv_gz_file:
        with gzip.open(csv_gz_file, 'rt') as csv_file:  # type: ignore
            yield csv.reader(cast(io.TextIOBase, csv_file), **csv_format_args), pathlib.Path(entry).stem


def _open_csv_from_zip(series_input: pathlib.Path, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with ZipFile(series_input, 'r') as zip_archive:
        for entry_name in zip_archive.namelist():
            LOG.debug('reading zip entry %s from %s', entry_name, series_input)
            if any(entry_name.endswith(suffix) for suffix in TIMESERIES_SUFFIXES):
                yield from _open_csv_gz_from_zip_entry(zip_archive, entry_name, **csv_format_args)
            else:
                yield from _open_csv_from_zip_entry(zip_archive, entry_name, **csv_format_args)


def _open_csv_from_zip_entry(archive: ZipFile, entry: str, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with archive.open(entry, 'r') as csv_zipped_file:
        yield csv.reader(io.TextIOWrapper(csv_zipped_file), **csv_format_args), pathlib.Path(entry).stem


def _open_csv_gz_from_zip_entry(archive: ZipFile, entry: str, **csv_format_args) -> Iterator[CSVReaderAndResource]:
    with archive.open(entry, 'r') as csv_zipped_file:
        with gzip.open(csv_zipped_file, 'rt') as csv_file:
            yield csv.reader(cast(io.TextIOBase, csv_file), **csv_format_args), pathlib.Path(entry).stem


def _open_csv_iterable(
    series_input: Union[Iterable[str], Iterable[Sequence[str]]], **csv_format_args
) -> Iterator[CSVReaderAndResource]:
    # inspect first item of iterable
    first_line = next(iter(series_input))
    if isinstance(first_line, str):
        # Iterable of strings, treat as unparsed csv data
        yield csv.reader(
            iter(cast(Iterable[str], series_input)),
            **csv_format_args
        ), None
    elif isinstance(first_line, Sequence):
        # Iterable of lists, treat as parsed csv data
        yield iter(cast(Iterable[Sequence[str]], series_input)), None
    else:
        raise ParserRequestError(
            f'Cannot read first line of a csv input:\n{first_line}'
        )
    return
