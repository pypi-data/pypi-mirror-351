"""Command line interface for the series service."""
from typing import Any, Dict, List, Union, TextIO
import sys
import io
import pathlib
import logging

from argparse import ArgumentParser, Namespace, RawTextHelpFormatter
from waylay.service.timeseries.tool import ResourceUpdateLevel

from waylay import WaylayClient
from waylay.service.timeseries.parser.model import (
    SeriesSettings, ArchiveType, TimestampFormat, Metric, Resource
)

from ._decorators import cli_exeption_decorator

LOG = logging.getLogger(__name__)

SERIES_COMMANDS = [CMD_EXPORT, CMD_IMPORT] = ['export', 'import']


def init_series_parser(parser: ArgumentParser):
    """Initialize the parser for the 'series' command."""
    if sys.version_info > (3, 7):
        series_cmd_parsers = parser.add_subparsers(
            help='Get or add timeseries data',
            dest='series_cmd',
            title='Series command',
            required=True
        )
    else:
        series_cmd_parsers = parser.add_subparsers(dest='series_cmd', title='Series command')

    init_series_export_parser(series_cmd_parsers.add_parser(
        CMD_EXPORT,
        description='Export series to a local file',
        help='Export series to a local file',
        formatter_class=RawTextHelpFormatter
    ))
    init_series_import_parser(series_cmd_parsers.add_parser(
        CMD_IMPORT,
        description='Import series from a local file',
        help='Import series from a local file',
        formatter_class=RawTextHelpFormatter
    ))
    return parser


def init_series_timestamp_parser(parser: ArgumentParser):
    """Initialize the parser for the timestamp filtering and mapping."""
    parser.add_argument(
        '-t', '--timestamp-format', dest='timestamp_format', nargs='?', default=TimestampFormat.ISO.value,
        type=TimestampFormat.lookup, choices=list(t.value for t in TimestampFormat),
        help=(
            'Specify a timestamp format for csv export rendering and csv import parsing.\n'
            + '\n'.join(f'- {t.value: <6}: {t.description}' for t in TimestampFormat)
        ),
    )
    parser.add_argument(
        '-z', '--timezone', dest='timestamp_timezone', metavar='TZ', nargs='?', default='UTC',
        help=(
            'Specify the timezone used for rendering iso-formatted timestamps,'
            "\nand for parsing inputs that do not specify a timezone."
        ),
    )
    parser.add_argument(
        '--from', dest='timestamp_from', metavar='FROM', nargs='?', default=None,
        help=(
            'Filter the series to have a timestamp equal to or greater than this one.'
        ),
    )
    parser.add_argument(
        '--until', dest='timestamp_until', metavar='UNTIL', nargs='?', default=None,
        help=(
            'Filter the series to have a timestamp strictly less than this one.'
        ),
    )


def init_series_export_parser(parser: ArgumentParser):
    """Initialize the parser for the 'series export' command."""
    parser.add_argument(
        '-r', '--resources', dest='resources', metavar='RESOURCE_ID[=resource_key]', nargs='+',
        help=(
            'Specify the resource ids to export.'
            "\nA resource id can be mapped with a 'RESOURCE_ID[=resource_key]' expression, with"
            "\n    'RESOURCE_ID' the resource id in waylay time series database"
            "\n    'resource_key' the value written to the csv file"
            '\nWhen specified, time series with resource ids not mentioned will be skipped.'
        ),
        required=True,
    )
    parser.add_argument(
        '-m', '--metrics', dest='metrics', metavar='METRIC_NAME[=metric_key]', nargs='+',
        help=(
            'Specify the metric names to export'
            "\nA metric name can be mapped with a 'METRIC_NAME[=metric_key]' expression, with"
            "\n    'METRIC_NAME' the metric name used in waylay time series database"
            "\n    'metric_key' the value used in the exported csv file "
            '(as metric header or value in a metric column)'
            '\nWhen specified, time series with metric name/keys not mentioned will be skipped.'
        ),
        required=True,
    )
    parser.add_argument(
        '-c', '--columns', dest='columns', metavar='COL[=name]',  nargs='*',
        help=(
            'Specify the output columns for the export.'
            '\n - resource[=column_name]'
            "\n     Include a 'resource' column for the resource ids."
            '\n     By default only present when multiple resources are exported.'
            "\n     'resource' will always include the resource column."
            "\n     'resource=' will always omit the resource column."
            "\n     'resource=office' will rename the resource column to 'office'."
            '\n - value[=column_name]'
            "\n     Include/rename a 'value' column for the series values."
            '\n     Setting this implies an import/export in a normalized format,'
            '\n     with a single metric per row.'
            '\n - metric[=column_name]'
            "\n     Include/rename a 'metric' column for the metric name."
            "\n     Not used unless the 'value' column is set."
            '\n - timestamp[=column_name]'
            "\n     Rename a 'timestamp' column for the timestamps."
            "\n     'timestamp=' will omit the default timestamp column."
        ),
    )
    parser.add_argument(
        '-o', '--output', dest='output', nargs='?', default=sys.stdout,
        help=(
            'Specify an output for the export (file or dir).\n'
            'Defaults to standard output (csv text).'
        ),
    )
    parser.add_argument(
        '-a', '--archive-type', dest='archive_type', nargs='?', default=None,
        type=ArchiveType.lookup, choices=list(t.value for t in ArchiveType),  # type: ignore
        help=(
            'Specify an archive type for the export.\n'
            + '\n'.join(f'- {t.value: <6}: {t.description}' for t in ArchiveType)
            + '\nIf not specified, the archive type is inferred from the output name or type.'
        ),
    )
    init_series_timestamp_parser(parser)
    parser.add_argument(
        '--per-resource', dest='per_resource', action="store_true", default=False,
        help=(
            'If set, export each resource in a seperate file.\n'
            'Does not work for single-file archive types (text, gz).'
        ),
    )
    parser.add_argument(
        '--per-metric', dest='per_metric', action="store_true", default=False,
        help=(
            'If set, export each metric in a seperate file.\n'
            'Does not work for single-file archive types (text, gz).'
        ),
    )
    parser.add_argument(
        '--silent', dest='silent', action="store_true", default=False,
        help=(
            "Minimize stderr output (no progress bar)."
        ),
    )


def init_series_import_parser(parser: ArgumentParser):
    """Initialize the parser for the 'series import' command."""
    parser.add_argument(
        'series', nargs='+',
        help=(
            'Specify an input for the import (file or dir).\n'
            "Use '-' to specify standard input (csv text)."
        )
    )
    parser.add_argument(
        '-n', '--name', dest='name', nargs='?', default=None,
        help=(
            'ETL import job name, used as prefix base name for the ETL import file.'
        ),
    )
    parser.add_argument(
        '-R', '--default-resource', metavar='RESOURCE_ID', dest='default_resource', nargs='?', default=None,
        help=(
            'A default resource id for this import. Only used when not specified in the import file.'
            '\nWhen not set, and not provided by the import file, the default resource name'
            "\nis inferred from the base name of the import file or from the '--name' argument."
        ),
    )
    parser.add_argument(
        '-M', '--default-metric', metavar='METRIC_NAME', dest='default_metric', nargs='?', default=None,
        help=(
            'A default metric name for this import. Only used when not specified as import data.'
        )
    )
    parser.add_argument(
        '-r', '--resources', dest='resources', metavar='RESOURCE_ID[=resource_key]', nargs='*',
        help=(
            'Filter and/or rename the resource ids in the import.'
            "\nA resource id can be mapped with a 'RESOURCE_ID[=resource_key]' expression, with"
            "\n    'RESOURCE_ID' the resource id written to the waylay time series database"
            "\n    'resource_key' the value used in the import csv file"
            '\nWhen specified, time series with resource id/keys not mentioned will be skipped.'
        ),
    )
    parser.add_argument(
        '-m', '--metrics', dest='metrics', metavar='METRIC_NAME[=metric_key]', nargs='*',
        help=(
            'Specify the metric names to import'
            "\nA metric name can be mapped with a 'METRIC_NAME[=metric_key]' expression, with"
            "\n    'METRIC_NAME' the metric name used in waylay time series database"
            "\n    'metric_key' the value used in the import csv file "
            '(as metric header or value in a metric column)'
            '\nWhen specified, time series with metric name/keys not mentioned will be skipped.'
        ),
    )
    parser.add_argument(
        '-c', '--columns', dest='columns', metavar='COLUMN[=column_name]',  nargs='*',
        help=(
            'Specify alternate column names in the import files.'
            "\nBy default, import csv files are expected to have a 'timestamp' column, and"
            "\n all other columns contain series with metric name in the header."
            '\n - resource[=resource_column_name]'
            "\n     Use the 'resource_column_name' (default 'resource') as keys for resource ids."
            "\n     If not set, any column named 'resource' will be used, or"
            "\n       the default resource key (see '--default-resource') will be used."
            "\n     E.g. 'resource=device' will expect a column named 'device' containing resource keys'."
            '\n - value[=value_column_name]'
            "\n     Use the 'value_column_name' (default 'value') column for the series values."
            '\n     Setting this implies an a normalized format with one metric per row.'
            '\n - metric[=metric_column_name]'
            "\n     Use the 'metric_column_name' (default 'metric') column for the series metric keys."
            "\n     Only relevant when 'value' column is set."
            "\n     When not set, any column 'metric' is used, or a"
            '\n     default metric name (see --default-metric) should be specified.'
            '\n - timestamp[=timestamp_column_name]'
            "\n     Use the 'timestamp_column_name' (default 'timestamp') column as series timestamp."
        ),
    )
    init_series_timestamp_parser(parser)
    parser.add_argument(
        '-T', '--temp-dir', dest='temp_dir', nargs='?', default=None,
        help=(
            'The local storage location to use in preparing the ETL file.\n'
            "Defaults to a system generated temp file with prefix 'etl-import'."
        ),
    )
    parser.add_argument(
        '--resource-update', dest='resource_update_level', nargs='?',
        type=ResourceUpdateLevel, default=ResourceUpdateLevel.ID,
        choices=list(level.value for level in ResourceUpdateLevel),
        help=(
            'Level of update of the waylay resource metadata after import.'
            '\n- none : Do not update resource metadata'
            '\n- id   : (default) Make sure the resource exists (id only)'
            '\n- all  : Create or update id, name and metrics metadata on the resource.'
        )
    )
    parser.add_argument(
        '--silent', dest='silent', action="store_true", default=False,
        help=(
            "Minimize stderr output (no progress bar)"
        ),
    )
    parser.add_argument(
        '--no-import', dest='no_import', action="store_true", default=False,
        help=(
            'Process the inputs without uploading to the timeseries database.'
            '\nOutputs the location of the (temporary) etl import file.'
        ),
    )


def init_series_import_timestamp_generation(parser: ArgumentParser):
    """Initialize the parser argument for generation/mapping of timestamps during import."""
    parser.add_argument(
        '--first', dest='timestamp_first', nargs='?', default=None,
        help=(
            'Forces the first timestamp, and increments'
            'the following timestamps with the same amount.'
        )
    )
    parser.add_argument(
        '--last', dest='timestamp_last', nargs='?', default=None,
        help=(
            'Forces the last timestamp, and increments'
            'the preceding timestamps with the same amount.'
        )
    )
    parser.add_argument(
        '--interval', dest='timestamp_interval', nargs='?', default=None,
        help=(
            'Ignores the input timestamps and writes data with fixed timestamp intervals.\n'
            "Requires '--first'."
        )
    )
    parser.add_argument(
        '--offset', dest='timestamp_offset', nargs='?', default=None,
        help=(
            'A time interval to add to the input timestamp.'
        )
    )


def handle_series_cmd(client: WaylayClient, args: Namespace) -> bool:
    """Execute a 'series' command."""
    if args.series_cmd == CMD_EXPORT:
        handle_series_export_cmd(client, args)
        return True
    elif args.series_cmd == CMD_IMPORT:
        handle_series_import_cmd(client, args)
        return True
    return False


def convert_metrics(metrics_arg: List[str]) -> List[Metric]:
    """Convert a metrics list argument."""
    try:
        return [
            Metric(name=parts[0], key=(parts[1] if len(parts) > 1 else parts[0]))
            for m in metrics_arg
            for parts in [m.split('=')]
        ]
    except ValueError as exc:
        raise ValueError(f'Invalid metrics specification: {metrics_arg}') from exc


def convert_resources(resources_arg: List[str]) -> List[Resource]:
    """Convert a resources list argument."""
    try:
        return [
            Resource(id=parts[0], key=(parts[1] if len(parts) > 1 else parts[0]))
            for r in resources_arg
            for parts in [r.split('=')]
        ]
    except ValueError as exc:
        raise ValueError(f'Invalid resources specification: {resources_arg}') from exc


@cli_exeption_decorator
def handle_series_export_cmd(client: WaylayClient, args: Namespace):
    """Execute the 'series export' command."""
    metrics = convert_metrics(args.metrics)
    resources = convert_resources(args.resources)
    column_names = create_column_arguments(args)
    if 'timestamp_column' not in column_names:
        column_names['timestamp_column'] = 'timestamp'

    series_settings = SeriesSettings(
        per_resource=args.per_resource,
        per_metric=args.per_metric,
        resources=resources,
        metrics=metrics,
        **column_names,
        timestamp_format=args.timestamp_format,
        timestamp_timezone=args.timestamp_timezone,
        timestamp_from=args.timestamp_from,
        timestamp_until=args.timestamp_until,
    )
    client.timeseries.etl_tool.export_series_as_csv(
        args.output,
        archive_type=args.archive_type,
        progress=not args.silent,
        settings=series_settings,
    )


@cli_exeption_decorator
def handle_series_import_cmd(client: WaylayClient, args: Namespace):
    """Execute the 'series import' command."""
    metrics = convert_metrics(args.metrics or []) or None
    resources = convert_resources(args.resources or []) or None
    column_names = create_column_arguments(args)

    series_settings = SeriesSettings(
        resources=resources,
        metrics=metrics,
        resource=args.default_resource,
        metric=args.default_metric,
        **column_names,
        timestamp_format=args.timestamp_format,
        timestamp_timezone=args.timestamp_timezone,
        timestamp_from=args.timestamp_from,
        timestamp_until=args.timestamp_until,
    )

    series_input: List[Union[io.TextIOBase, pathlib.Path]] = [
        TextIOPeekReader(reader=sys.stdin) if s == '-' else pathlib.Path(s)
        for s in args.series
    ]
    progress = not args.silent
    etl_import = client.timeseries.etl_tool.prepare_import(
        *series_input,
        settings=series_settings,
        name=args.name,
        temp_dir=args.temp_dir,
        progress=progress
    )
    if args.no_import:
        print(etl_import.import_file.path)
        return

    client.timeseries.etl_tool.initiate_import(
        etl_import,
        resource_update_level=args.resource_update_level,
        progress=progress
    )


COLUMN_NAMES = ('timestamp', 'metric', 'resource', 'value')


def create_column_arguments(args: Namespace):
    """Create a dictionary out of column arguments."""
    column_names: Dict[str, Any] = {}
    if args.columns:
        for col_spec in args.columns:
            if '=' not in col_spec:
                col_spec = f'{col_spec}={col_spec}'
            try:
                column, name = col_spec.split('=')
                if column not in COLUMN_NAMES:
                    raise ValueError(f'Invalid column specification: {col_spec}')
                column_names[f'{column}_column'] = name or None
            except ValueError as exc:
                raise ValueError(f'Invalid column specification: {col_spec}') from exc
    return column_names


class TextIOPeekReader(io.TextIOBase):
    """A reader around stdin (or other readonly stream) that allows to peek the first n lines."""

    def __init__(self, peek_limit: int = 2, reader: TextIO = sys.stdin):
        """Create a TextIOPeekReader."""
        super().__init__()
        self.reader = reader
        self.peek_reads: List[str] = []
        self.peek_limit = peek_limit
        self.line_count = 0

    def readline(self):
        """Read a line from underlying text stream, buffering the first n."""
        line_count = self.line_count
        self.line_count += 1
        if line_count <= self.peek_limit:
            if line_count < len(self.peek_reads):
                return self.peek_reads[line_count]
            line = self.reader.readline()
            self.peek_reads.append(line)
            return line
        return self.reader.readline()

    def seek(self, offset: int, whence: int = 0):
        """If only first lines are read, reset to read from buffer."""
        line_count = self.line_count
        self.line_count = 0
        if whence == 0 and offset == 0 and line_count <= self.peek_limit:
            return
        # seek above the peek limit, try (and probably fail) to seek the underlying stream
        self.reader.seek(offset, whence)
        self.peek_reads = []
