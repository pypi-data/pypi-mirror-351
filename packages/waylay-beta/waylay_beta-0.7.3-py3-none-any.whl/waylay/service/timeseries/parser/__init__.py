"""Utilities to parse and render ETL timeseries files."""
from typing import (
    Optional, Any
)
import gzip
import csv
from dataclasses import replace

import pandas as pd
from tqdm.std import tqdm

from waylay.exceptions import RequestError

from .model import (
    Metric,
    Resource,
    SeriesSettings,
    ETLFile,
    WaylayETLSeriesImport,

    SeriesInput,
    SeriesIterator,
    ETL_IMPORT_COLUMN_NAMES,
    render_timestamp_zulu,
    ParserRequestError,
)
from .import_csv import (
    MeasurementsStoreType,
    prepare_settings_csv,
    create_import_series_provider
)
from .import_dataframe import (
    prepare_settings_dataframe,
    iter_timeseries_dataframe
)
from .etlfile import (
    read_etl_import_as_stream,
    read_etl_import,
    dataframe_from_iterator,
    list_resources,
)

from .export_series import (
    export_csv,
    export_csv_to_tar_archive,
    export_csv_to_zip_archive,
    export_csv_to_dir,
    create_export_series_provider,
)


def iter_timeseries(
    *input_data: SeriesInput,
    settings: SeriesSettings,
    progress: bool = False,
    measurements_store: MeasurementsStoreType = MeasurementsStoreType.SPOOLED
) -> SeriesIterator:
    """Create a SeriesIterator for the given input source and settings."""
    if not input_data:
        raise AttributeError('input_data required.')
    if isinstance(input_data[0], pd.DataFrame):
        yield from iter_timeseries_dataframe(*input_data, settings=settings, progress=progress)
    else:
        with create_import_series_provider(
            *input_data, settings=settings, progress=progress, measurements_store=measurements_store
        ) as series_provider:
            if progress:
                with tqdm(
                    total=series_provider.row_count, unit='rows',
                    unit_scale=True, unit_divisor=1
                ) as tqdm_progress:
                    for (resource_id, metric_name), measurements in series_provider.items():
                        tqdm_progress.update()
                        yield resource_id, metric_name, iter(measurements)
            else:
                for (resource_id, metric_name), measurements in series_provider.items():
                    yield resource_id, metric_name, iter(measurements)


def prepare_etl_import(
    *series_input: SeriesInput,
    import_file: Optional[ETLFile] = None,
    settings: Optional[SeriesSettings] = None,
    **settings_args: Any
) -> WaylayETLSeriesImport:
    """Update the mapping settings by extracting metadata from an input source."""
    import_file = import_file or ETLFile()
    settings = settings or SeriesSettings()
    if settings_args:
        settings = replace(settings, **settings_args)

    # input settings validation
    etl_import = WaylayETLSeriesImport(
        series_input=series_input,
        settings=settings,
        import_file=import_file
    )

    # input series validation
    if not series_input:
        raise AttributeError('series_input required.')
    if isinstance(series_input[0], pd.DataFrame):
        if len(series_input) > 1:
            raise AttributeError('Multiple dataframe series_input not yet supported.')
        settings = prepare_settings_dataframe(series_input[0], settings=settings)
        etl_import = replace(etl_import, settings=settings)
    else:
        settings = prepare_settings_csv(*series_input, settings=settings)
        etl_import = replace(etl_import, settings=settings)
    return etl_import


def create_etl_import(
    etl_import: WaylayETLSeriesImport,
    progress: bool = True,
    measurements_store: MeasurementsStoreType = MeasurementsStoreType.SPOOLED
) -> WaylayETLSeriesImport:
    """Create an ETL import file from the given input."""
    file_path = etl_import.import_file.path
    if file_path.exists():
        raise RequestError(
            f'The file {file_path} already exists. '
            'Please remove or specify another etl-import file name.'
        )

    timeseries_data = iter_timeseries(
        *etl_import.series_input,
        settings=etl_import.settings,
        progress=progress,
        measurements_store=measurements_store
    )
    with gzip.open(file_path, 'wt') as csv_file:
        writer = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(ETL_IMPORT_COLUMN_NAMES)
        for resource, metric, measurements in timeseries_data:
            if not etl_import.settings.skip_empty_values:
                measurements_it = (
                    (t, v) for t, v in measurements if t is not None
                )
            else:
                measurements_it = (
                    (t, v) for t, v in measurements if t is not None and v is not None and v != ''
                )

            for timestamp, value in measurements_it:
                writer.writerow([
                    resource,
                    metric,
                    render_timestamp_zulu(timestamp),
                    value
                ])
    return etl_import
