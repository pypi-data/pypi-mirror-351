"""Module that implements export readers for waylay timeseries data."""
from datetime import datetime
from dataclasses import replace
from io import TextIOBase, IOBase
from os import PathLike
from tarfile import TarFile
from time import time
from typing import (
    Any, Callable, Dict, Iterator, Iterable, List,
    Optional, Sequence, TextIO, Tuple, Union, IO,
    cast, BinaryIO
)
from zipfile import ZipFile

import collections.abc
import pathlib
import gzip
import csv
import urllib.parse
import logging
import os

import pandas as pd

from waylay.service.data.series import SeriesResource

from .model import (
    ArchiveType, CSVWriteable, Measurement, MeasurementIterator,
    SeriesIterator, SeriesProvider, SeriesSettings, CSVOutput, TimestampFormat
)
from .util import (
    NonClosingTextIOWrapper,
    WrappeableSpooledTemporaryFile,
)
LOG = logging.getLogger(__name__)
DEFAULT_EXPORT_PAGE_SIZE = 2000
DEFAULT_SPOOL_MAX_SIZE = 2 << 18
TS_FORMAT_MILLIS = TimestampFormat.MILLIS.formatter()


def create_export_series_provider(
    settings: SeriesSettings, series_api: SeriesResource
) -> SeriesProvider:
    """Create a series provider from the waylay api for the given settings."""
    return PagingExportSeriesProvider(settings, series_api)


class PagingExportSeriesProvider(collections.abc.Mapping):
    """A series provider that uses paging exports from the waylay series api."""

    def __init__(self, settings: SeriesSettings, series_api: SeriesResource):
        """Create an export series provider."""
        self.settings = settings
        self.series_api = series_api
        self._keys = [
            (resource.id, metric.name)
            for resource in settings.iter_resources()
            for metric in settings.iter_metrics()
        ]

    def __iter__(self):
        """Iterate over the (resource, metric) keys of this provider."""
        return iter(self._keys)

    def __len__(self):
        """Get the number of requested (resource,metric) combinations."""
        return len(self._keys)

    def __getitem__(self, resource_metric: Tuple[str, str]) -> Iterable[Measurement]:
        """Create an measurement iterable for a given resource, metric."""
        resource, metric = resource_metric
        provider = self

        class _MeasurementIterable():
            def __iter__(self) -> Iterator[Measurement]:
                return provider._iter_single_series_export(resource, metric)

        return _MeasurementIterable()

    def _iter_single_series_export(
        self,
        resource_id: str, metric: str,
        page_size: int = DEFAULT_EXPORT_PAGE_SIZE
    ) -> MeasurementIterator:
        """Paging iterator over the specified resource and metric."""
        params: Dict[str, Any] = {
            'from': 0,
            'order': 'ascending',
            'limit': page_size
        }
        settings = self.settings
        timestamp_from = settings.get_timestamp_from()
        if timestamp_from:
            params['from'] = TS_FORMAT_MILLIS(timestamp_from)
        timestamp_until = settings.get_timestamp_until()
        if timestamp_until:
            params['until'] = TS_FORMAT_MILLIS(timestamp_until)

        while True:
            LOG.debug(f'fetching a page of series for %s:%s', resource_id, metric)
            resp = self.series_api.export(resource_id, metric, params=params, select_path=None)
            if 'series' in resp:
                for item in resp['series']:
                    yield (
                        pd.Timestamp(item[0], unit='ms', tz='UTC'),
                        item[1]
                    )
            next_link = resp.get('_links', {}).get('next', {}).get('href')
            if not next_link:
                return
            next_query = urllib.parse.urlparse(next_link).query
            params = urllib.parse.parse_qs(next_query)


def _iter_settings(settings: SeriesSettings):
    if settings.per_resource:
        for resource in settings.iter_resources():
            name = f'{settings.name}-{resource.id}' if settings.name else resource.id
            entry_settings = replace(
                settings, name=name, resource=resource.id, per_resource=False
            )
            yield from _iter_settings(entry_settings)
    elif settings.per_metric:
        for metric in settings.iter_metrics():
            name = f'{settings.name}-{metric.name}' if settings.name else metric.name
            entry_settings = replace(
                settings, name=name, metric=metric.name, per_metric=False
            )
            yield from _iter_settings(entry_settings)
    else:
        yield settings.name or 'series', settings


ARCHIVE_DEFAULT_EXTENSIONS = {
    '.zip': 'zip'
}


def export_csv(
    output: CSVOutput,
    settings: SeriesSettings,
    series: SeriesProvider,
    archive_type: Optional[ArchiveType] = None,
    progress: bool = True,
):
    """Export a series iterator to a CSV file or archive."""
    if isinstance(output, (str, PathLike)):
        mkdirs = os.fspath(output).endswith('/')
        output = pathlib.Path(output)
        if mkdirs:
            output.mkdir(parents=True, exist_ok=True)
        supported_archive_types = ArchiveType.supported_for(output, settings.per_resource or settings.per_metric)
    elif isinstance(output, ZipFile):
        supported_archive_types = [ArchiveType.ZIP]
    elif isinstance(output, TarFile):
        supported_archive_types = [ArchiveType.TAR, ArchiveType.TAR_GZ]
    elif isinstance(output, TextIOBase):
        supported_archive_types = [ArchiveType.TEXT]
    elif isinstance(output, IOBase):
        supported_archive_types = [
            at for at in ArchiveType
            if at.supports_multiple_files or not (settings.per_resource or settings.per_metric)
            if not at.is_dir_type
        ]
    elif isinstance(output, CSVWriteable):
        supported_archive_types = [ArchiveType.TEXT]
    else:
        supported_archive_types = []

    if not supported_archive_types:
        raise TypeError(f'Unsupported output type {type(output)}')

    archive_type = archive_type or supported_archive_types[0]
    LOG.debug('output = %r', output)
    LOG.debug('archive_type = %r', archive_type)

    if (settings.per_resource or settings.per_metric) and not archive_type.supports_multiple_files:
        raise ValueError(f'Archive type `{archive_type}` does not support multiple outputs.')

    if archive_type not in supported_archive_types:
        raise ValueError(f'Archive type `{archive_type}` not supported for given output')

    if archive_type in (ArchiveType.TEXT, ArchiveType.GZ):
        LOG.info('exporting to single output: %s', output)
        if isinstance(output, TextIOBase):
            return export_csv_to_file(output, settings, series)
        if isinstance(output, IOBase):
            if archive_type is ArchiveType.GZ:
                with gzip.open(output, mode='wt') as text_output:
                    return export_csv_to_file(cast(TextIO, text_output), settings, series)
            return export_csv_to_file(NonClosingTextIOWrapper(cast(IO[bytes], output)), settings, series)
        if isinstance(output, CSVWriteable):
            return export_csv_to_file(output, settings, series)
        if isinstance(output, pathlib.Path):
            if archive_type is ArchiveType.GZ:
                with gzip.open(output, mode='wt') as text_output:
                    return export_csv_to_file(text_output, settings, series)
            with open(output, 'wt') as text_output:
                return export_csv_to_file(text_output, settings, series)
        raise TypeError(f'Unsupported output type for archive type {archive_type}')  # pragma: no cover

    if archive_type in (ArchiveType.DIR, ArchiveType.DIR_GZ):
        LOG.info('exporting to directory: %s', output)
        if isinstance(output, pathlib.Path):
            return export_csv_to_dir(
                output, settings, series,
                compress=archive_type == ArchiveType.DIR_GZ
            )
        raise TypeError(f'Unsupported output type for archive type {archive_type}')  # pragma: no cover

    if archive_type is ArchiveType.ZIP:
        LOG.info('exporting to zip archive: %s', output)
        if isinstance(output, ZipFile):
            return export_csv_to_zip_archive(output, settings, series)
        if isinstance(output, pathlib.Path):
            with ZipFile(output, mode='w') as zip_file:
                return export_csv_to_zip_archive(zip_file, settings, series)
        if isinstance(output, IOBase) and not isinstance(output, TextIOBase):
            zip_file = ZipFile(cast(IO[bytes], output), mode='w')
            return export_csv_to_zip_archive(zip_file, settings, series)
        raise TypeError(f'Unsupported output type for archive type {archive_type}')  # pragma: no cover

    if archive_type in (ArchiveType.TAR, ArchiveType.TAR_GZ):
        LOG.info('exporting to tar archive: %s', output)
        if isinstance(output, TarFile):
            return export_csv_to_tar_archive(output, settings, series)
        tar_mode = 'w' if archive_type is ArchiveType.TAR else 'w:gz'
        if isinstance(output, pathlib.Path):
            with TarFile.open(output, mode=tar_mode) as tar_file:
                return export_csv_to_tar_archive(tar_file, settings, series)
        if isinstance(output, IOBase) and not isinstance(output, TextIOBase):
            tar_file = TarFile.open(fileobj=cast(IO[bytes], output), mode=tar_mode)
            return export_csv_to_tar_archive(tar_file, settings, series)
        raise TypeError(f'Unsupported output type for archive type {archive_type}')  # pragma: no cover


def export_csv_to_dir(
    csv_dir: Union[str, PathLike], settings: SeriesSettings,
    series: SeriesProvider, compress: bool = False
):
    """Export a series provider to a directory csv files."""
    dir_path = pathlib.Path(csv_dir)
    # raises a File exists if `dir` is a file
    dir_path.mkdir(parents=True, exist_ok=True)
    for entry_name, entry_settings in _iter_settings(settings):
        if compress:
            file_name = dir_path / f'{entry_name}.csv.gzip'
            LOG.info('exporting to compressed file: %s', file_name)
            with gzip.open(file_name, 'wt') as file:
                export_csv_to_file(file, entry_settings, series)
        else:
            file_name = dir_path / f'{entry_name}.csv'
            LOG.info('exporting to uncompressed file: %s', file_name)
            with open(dir_path / f'{entry_name}.csv', 'w') as file:
                export_csv_to_file(file, entry_settings, series)


def export_csv_to_zip_archive(
    zip_file: ZipFile, settings: SeriesSettings,
    series: SeriesProvider
):
    """Export a series provider to a zip archive of csv files."""
    for entry_name, entry_settings in _iter_settings(settings):
        entry_file_name = f'{entry_name}.csv'
        LOG.info('writing zip entry: %s', entry_file_name)
        with zip_file.open(entry_file_name, 'w') as zip_file_entry:
            export_csv_to_file(NonClosingTextIOWrapper(zip_file_entry), entry_settings, series)


def export_csv_to_tar_archive(
    tar_file: TarFile, settings: SeriesSettings, series: SeriesProvider
):
    """Export a series provider to a tar archive of csv files per resource."""
    for entry_name, entry_settings in _iter_settings(settings):
        entry_file_name = f'{entry_name}.csv'
        LOG.info('writing tar entry: %s', entry_file_name)
        with WrappeableSpooledTemporaryFile(mode='wb+', max_size=DEFAULT_SPOOL_MAX_SIZE) as csv_buffer:
            export_csv_to_file(NonClosingTextIOWrapper(csv_buffer), entry_settings, series)
            tar_info = TarFile.tarinfo(f'{entry_name}.csv')
            tar_info.mtime = int(time())
            tar_info.size = csv_buffer.tell()
            csv_buffer.seek(0)
            tar_file.addfile(tar_info, csv_buffer)


def export_csv_to_file(
    output: CSVWriteable, settings: SeriesSettings, series_provider: SeriesProvider
):
    """Export a series provider to a CSV output stream according to the settings."""
    if settings.value_column:
        _export_csv_values(output, settings, series_provider)
    else:
        _export_csv_columns(output, settings, series_provider)


def _export_csv_values(
    output: CSVWriteable, settings: SeriesSettings, series_provider: SeriesProvider
):
    selected_resource_ids = [r.id for r in settings.iter_resources()]
    selected_metric_names = [m.name for m in settings.iter_metrics()]

    header = []
    write_resource = False
    write_metric = False
    write_timestamp = False
    format_timestamp = settings.get_timestamp_formatter()
    if settings.resource_column or len(selected_resource_ids) > 1:
        write_resource = True
        header.append(settings.resource_column or 'resource')
    if settings.metric_column or len(selected_metric_names) > 1:
        write_metric = True
        header.append(settings.metric_column or 'metric')
    if settings.timestamp_column:
        write_timestamp = True
        header.append(settings.timestamp_column or 'timestamp')
    header.append(settings.value_column or 'value')
    csv_writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    if settings.write_csv_header:
        csv_writer.writerow(header)
        LOG.debug('csv header = %r', header)
    for (resource_id, metric_name), measures in series_provider.items():
        if resource_id not in selected_resource_ids:
            continue
        if metric_name not in selected_metric_names:
            continue
        rec = []
        if write_resource:
            rec.append(settings.resource_for(resource_id).key_or_id)
        if write_metric:
            rec.append(settings.metric_for(metric_name).key_or_name)
        if write_timestamp:
            for timestamp, value in measures:
                csv_writer.writerow((*rec, format_timestamp(timestamp), str(value)))
        else:
            for timestamp, value in measures:
                csv_writer.writerow((*rec, str(value)))


def _export_csv_columns(output: CSVWriteable, settings: SeriesSettings, series: SeriesProvider):
    selected_resource_ids = [r.id for r in settings.iter_resources()]
    LOG.debug('selected resource ids = %r', selected_resource_ids)
    selected_metric_names = [m.name for m in settings.iter_metrics()]
    LOG.debug('selected metric names = %r', selected_metric_names)

    header = []
    write_timestamp = False
    write_resource = False
    format_timestamp = settings.get_timestamp_formatter()
    if settings.resource_column or len(selected_resource_ids) > 1:
        write_resource = True
        header.append(settings.resource_column or 'resource')
    if settings.timestamp_column:
        write_timestamp = True
        header.append(settings.timestamp_column or 'timestamp')
    header.extend([m.key_or_name for m in settings.iter_metrics()])

    csv_writer = csv.writer(output, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    LOG.debug('csv header = %r', header)
    if settings.write_csv_header:
        csv_writer.writerow(header)
    for resource_id in selected_resource_ids:
        resource_key = settings.resource_for(resource_id).key_or_id
        row_iterator = _merge_iterators(
            *(
                iter(series.get((resource_id, metric_name), []))
                for metric_name in selected_metric_names
            ),
            format_timestamp=format_timestamp if write_timestamp else None
        )
        if write_resource:
            for row in row_iterator:
                csv_writer.writerow((resource_key, *row))
        else:
            for row in row_iterator:
                csv_writer.writerow(row)


def _merge_iterators(
    *measure_iterators: MeasurementIterator,
    format_timestamp: Optional[Callable[[datetime], Any]],
) -> Iterator[Sequence[Any]]:
    """Merge a sequence of MeasurementIterators to a sequence of csv output records.

    Each iterator is assumed to be time-ordered.
    Each different timestamp will yield a seperate row.
    """
    next_measurements = list(next(it, None) for it in measure_iterators)
    while True:
        try:
            current_timestamp = min(m[0] for m in next_measurements if m is not None)
        except ValueError:
            # no timestamps left
            return
        curr_record: List[Optional[Any]] = [format_timestamp(current_timestamp)] if format_timestamp else []
        for idx, measurement in enumerate(next_measurements):
            if measurement is None:
                curr_record.append(None)
                continue
            timestamp, value = measurement
            if timestamp == current_timestamp:
                curr_record.append(value)
                next_measurements[idx] = next(measure_iterators[idx], None)
            else:
                curr_record.append(None)
        yield curr_record
