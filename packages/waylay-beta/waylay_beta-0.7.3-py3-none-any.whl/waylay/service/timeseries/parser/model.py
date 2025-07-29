"""Model objects for the timeseries tool."""
__docformat__ = "google"

from tarfile import TarFile
from typing import (
    Optional, Sequence, Union,
    Tuple, Iterator, Iterable, Any,
    Mapping, SupportsInt,
    Callable, IO, List
)

try:
    from typing import Protocol, runtime_checkable
except ImportError:  # pragma: no cover
    # typing.Protocol is a 3.8 feature ...
    # ... but typing_extensions provides forward compatibility.
    from typing_extensions import Protocol, runtime_checkable  # type: ignore

from datetime import datetime, timedelta, tzinfo
from enum import Enum
import os
import io
import re
import sys
import tempfile
from pathlib import Path

from dataclasses import dataclass, field, asdict, replace
from zipfile import ZipFile
import pandas as pd
import isodate
import pytz

from waylay.exceptions import RequestError

if sys.version_info > (3, 7):
    Pattern = re.Pattern  # pylint: disable=no-member
else:
    Pattern = Any

ETL_IMPORT_BUCKET = 'etl-import'
ETL_IMPORT_UPLOAD_PREFIX = 'upload/'
METRIC_PREFIX = 'waylay.resourcemessage.metric.'
METRIC_PREFIX_LENGTH = len(METRIC_PREFIX)

RESOURCE_COLUMN, METRIC_COLUMN, TIMESTAMP_COLUMN, VALUE_COLUMN = \
    ETL_IMPORT_COLUMN_NAMES = ['resource', 'metric', 'timestamp', 'value']
RESOURCE_IDX, METRIC_IDX, TIMESTAMP_IDX, VALUE_IDX = range(4)

MeasurementValue = Union[str, int, float, bool, None]

Measurement = Tuple[datetime, MeasurementValue]
MeasurementIterator = Iterator[Measurement]
SeriesProvider = Mapping[Tuple[str, str], Iterable[Measurement]]
SeriesIterator = Iterator[Tuple[str, str, MeasurementIterator]]

CSVReader = Iterator[Sequence[str]]
CSVReaderAndResource = Tuple[CSVReader, Optional[str]]
PathLike = Union[str, os.PathLike]

fromisoformat = datetime.fromisoformat

MAX_EPOCH_SECONDS = 9223000000  # '2262-04-07 16:26:40+0000'
MAX_EPOCH_MILLIS = MAX_EPOCH_SECONDS * 1000
MAX_EPOCH_MICROS = MAX_EPOCH_MILLIS * 1000
MAX_EPOCH_NANOS = MAX_EPOCH_MICROS * 1000


def parse_timestamp_unix(epoch: Union[str, SupportsInt]) -> pd.Timestamp:
    """Convert a unix epoch to datetime, automatically recognising ranges.

    Assumes that the represented timestamps are before '2262-04-07 16:26:40+0000'
    and after '1970-04-17 17:56:40+0000' (when not using seconds unit).
    (Limitation from 64-bit nanosecond representation used in pandas).
    """
    int_epoch = int(epoch)
    if int_epoch <= MAX_EPOCH_SECONDS:
        # use float to preserve fractional seconds
        # in smaller units, use int to have predictable rounding
        return pd.Timestamp(float(epoch), unit='s')  # type: ignore
    if int_epoch <= MAX_EPOCH_MILLIS:
        return pd.Timestamp(int_epoch, unit='ms')
    if int_epoch <= MAX_EPOCH_MICROS:
        return pd.Timestamp(int_epoch, unit='us')
    if int_epoch <= MAX_EPOCH_NANOS:
        return pd.Timestamp(int_epoch, unit='ns')
    raise ValueError(f'Not a supported unix epoch: {epoch}')


def _detect_timestamp_unix_unit(epoch: Union[str, SupportsInt]) -> 'TimestampFormat':
    """Detect the unix epoch formatter for  a give example timestamp value."""
    int_epoch = int(epoch)
    if int_epoch <= MAX_EPOCH_SECONDS:
        # use float to preserve fractional seconds
        # in smaller units, use int to have predictable rounding
        return TimestampFormat.SECONDS
    if int_epoch <= MAX_EPOCH_MILLIS:
        return TimestampFormat.MILLIS
    if int_epoch <= MAX_EPOCH_MICROS:
        return TimestampFormat.MICROS
    if int_epoch <= MAX_EPOCH_NANOS:
        return TimestampFormat.NANOS
    raise ValueError(f'Not a supported unix epoch: {epoch}')


def parse_timestamp_auto(value: Union[str, SupportsInt]) -> pd.Timestamp:
    """Convert a value to a timestamp, trying epoch or ISO representations."""
    try:
        return parse_timestamp_unix(value)
    except ValueError:
        return pd.Timestamp(value)


class ParserRequestError(RequestError):
    """Request validation errors in the timeseries etl parser utilities."""


def try_parse_float(value: str) -> Union[float, str]:
    """Parse a string to a float value or return the orignal value."""
    try:
        return float(value)
    except ValueError:
        return value


def parse_float(value: str) -> Optional[float]:
    """Parse a string to a float value or return None."""
    try:
        return float(value)
    except ValueError:
        return None


def try_parse_int(value: str) -> Union[int, str]:
    """Parse a string to a int value or return the orignal value."""
    try:
        return int(float(value))
    except ValueError:
        return value


def parse_int(value: str) -> Optional[int]:
    """Parse a string to a int value or return None."""
    try:
        return int(float(value))
    except ValueError:
        return None


def try_parse_bool(value: str) -> Union[str, bool]:
    """Parse a string to a boolean value or return the orignal value."""
    lower_value = value.lower()
    if lower_value in ['false', 'no', 'n', '0']:
        return False
    if lower_value in ['true', 'yes', 'y', '1']:
        return True
    return value


def parse_bool(value: str) -> Optional[bool]:
    """Parse a string to a boolean value or return None."""
    value = value.lower()
    if value in ['false', 'no', 'n', '0']:
        return False
    if value in ['true', 'yes', 'y', '1']:
        return True
    return None


PARSERS_BY_VALUE_TYPE = {
    'float': parse_float,
    'double': parse_float,
    'string': lambda x: x,
    'bool': parse_bool,
    'integer': parse_int,
}

TIMESTAMP_COLUMN_NAMES = [TIMESTAMP_COLUMN, 'time', 'date']


def render_timestamp_zulu(timestamp: datetime) -> str:
    """Render a timestamp into the format used by the ETL service."""
    return timestamp.isoformat().replace('+00:00', 'Z')


def parse_timestamp(iso_timestamp: str) -> datetime:
    """Parse a timestamp from the format used by the ETL service."""
    return fromisoformat(iso_timestamp.replace('Z', '+00:00'))


def parse_interval(interval: Optional[Union[str, pd.Timedelta, timedelta]]) -> Optional[timedelta]:
    """Parse a str to a time interval, supports ISO8601 durations."""
    if interval is None or isinstance(interval, timedelta):
        return interval

    try:
        if isinstance(interval, str) and 'P' in interval:
            return isodate.parse_duration(interval)
        return pd.Timedelta(interval).to_pytimedelta()

    except ValueError as exc:
        raise ParserRequestError(f'Invalid interval: {exc}') from exc


RESOURCE_METADATA_KEY = dict(
    value_type='valueType',
    metric_type='metricType'
)


@dataclass
class Metric:
    """Metadata for a metric (univariate series) within a dataset.

    This holds both specifications inferred from the dataset, as
    given explicitely by the caller.

    Attributes:
        name                The metric name that should be used in waylay
        key                 The key used in the input data set
        value_parser        The (python) parser for this value when reading from csv, e.g. `float`

    Descriptive Attributes:
        value_type          The (javascript) value_type that for this value
        metric_type         The type of metric (`gauge`, `counter`, `rate`, `timestamp` )
        unit                The unit
        description
    """

    name: str
    key: Optional[str] = None
    value_parser: Optional[Callable[[str], MeasurementValue]] = None

    description: Optional[str] = None
    value_type: Optional[str] = None
    metric_type: Optional[str] = None
    unit: Optional[str] = None

    def __post_init__(self):
        """Remove legacy prefix from name."""
        if self.name.startswith(METRIC_PREFIX):
            if self.key is None:
                self.key = self.name
            self.name = self.name[METRIC_PREFIX_LENGTH:]

    @property
    def key_or_name(self):
        """Get the data key for this metric, defaulting to the metric name."""
        return self.key or self.name

    def get_value_parser(self) -> Callable[[str], MeasurementValue]:
        """Get the parser callback for this metric."""
        if self.value_parser:
            return self.value_parser
        if not self.value_type:
            return try_parse_float
        return PARSERS_BY_VALUE_TYPE.get(self.value_type, try_parse_float)

    def to_dict(self):
        """Convert to a json object representation.

        This format complies with how metric metadata is stored in the Waylay Resource metadata.
        """
        return {
            RESOURCE_METADATA_KEY.get(key, key): value
            for key, value in asdict(self).items()
            if key not in ['key', 'value_parser']
            if value is not None
        }

    def __repr__(self) -> str:
        """Render as string."""
        if self.key:
            return f'{self.name} as {self.key}'
        return self.name


@dataclass
class Resource:
    """Metadata for a resource (owning entity of series) within a dataset.

    This holds both specifications inferred from the dataset,
    as given explicitely by the caller.

    Attributes:
        id:     The resource id that should be used in waylay
        key:    The key used in the input data set

    Descriptive Attributes:
        name:   The resource name that should be used in waylay
        description: A string description of the resource
        metrics:
            Metadata documentation on the series metrics
            that can be uploaded for this resource.
    """

    id: str
    key: Optional[str] = None

    description: Optional[str] = None
    name: Optional[str] = None
    metrics: Optional[Sequence[Metric]] = None

    @property
    def key_or_id(self):
        """Get the data key for this resource, defaulting to the resource id."""
        return self.key or self.id

    def to_dict(self):
        """Convert to a json object representation.

        This format complies with how resource metadata is stored in the Waylay Resource metadata.
        """
        resource_repr = {
            key: value for key, value in asdict(self).items()
            if key not in ['metrics']
            if value is not None
        }
        if 'name' not in resource_repr:
            resource_repr['name'] = self.id
        if self.metrics:
            resource_repr['metrics'] = [m.to_dict() for m in self.metrics]  # pylint: disable=not-an-iterable
        return resource_repr

    def with_metrics(self, metrics: Sequence[Metric]) -> 'Resource':
        """Return a copy of this description object with the given metrics instead."""
        return replace(self, metrics=metrics)

    def __repr__(self) -> str:
        """Render as string."""
        if self.key:
            return f'{self.id} as {self.key}'
        return self.id


class TimestampFormat(str, Enum):
    """Default timestamp formats for input and output."""

    ISO = (
        'iso', 'ISO8601 timestamp',
        '2020-09-17T01:38:59+00:00', r'^iso.*',
        # pd.Timestamp.fromisoformat, ==> cannot parse timezones?
        # fromisoformat # ==> cannot localize to UTC
        pd.Timestamp,  # OK, but parses a lot of other formats
        lambda t: t.isoformat(),
        True
    )
    SECONDS = (
        's', 'Unix seconds epoch', 1631099086, r'^s.*',
        lambda v: pd.Timestamp(float(v), unit='s', tz=pytz.UTC),
        lambda t: int(t.timestamp())
    )
    MILLIS = (
        'ms', 'Unix milliseconds epoch', 1631099086346, r'^(ms|mil).*',
        lambda v: pd.Timestamp(int(v), unit='ms', tz=pytz.UTC),
        lambda t: int(t.timestamp() * 1000)
    )
    MICROS = (
        'us', 'Unix microseconds epoch',  1631099086234123, r'^(u|µ|micr).*',
        lambda v: pd.Timestamp(int(v), unit='us', tz=pytz.UTC),
        lambda t: int(t.timestamp() * 1000000)
    )
    NANOS = (
        'ns', 'Unix nanosecond epoch', 1631099086432532154, r'^(ns|nano).*',
        lambda v: pd.Timestamp(int(v), unit='ns', tz=pytz.UTC),
        lambda t: int(t.timestamp() * 1000000000)
    )
    UNIX = (
        'unix', 'Unix epoch with automatic unit detection. Renders milliseconds.',
        1631099086346, r'^(un|ep).*',
        parse_timestamp_unix,
        lambda t: int(t.timestamp() * 1000)
    )
    AUTO = (
        'auto', 'Parse numeric value as unix epoch or ISO. Render ISO timestamp',
        '2020-09-17T01:38:59+00:00', r'^auto.*',
        parse_timestamp_auto,
        lambda t: t.isoformat(),
    )

    description: str
    example: Any
    _spec_matcher: Pattern
    # wrapping in a tuple to avoid mypy interpreting callable members as methods
    _parse: Tuple[Callable[[Any], datetime]]
    _format: Tuple[Callable[[datetime], Any]]
    _timezone_dependent: bool

    def __new__(
        cls,
        value: str,
        description: str,
        example: Any,
        spec_matcher: str,
        parse_method: Callable[[Any], pd.Timestamp],
        format_method: Callable[[pd.Timestamp], Any],
        timezone_dependent: bool = False,
    ):
        """Construct an enum value.

        See https://docs.python.org/3/library/enum.html#when-to-use-new-vs-init.
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        obj.example = example
        obj._parse = (parse_method,)
        obj._format = (format_method,)
        obj._spec_matcher = re.compile(spec_matcher, re.RegexFlag.IGNORECASE)
        obj._timezone_dependent = timezone_dependent
        return obj

    @classmethod
    def lookup(cls, spec: Union[str, 'TimestampFormat']) -> 'TimestampFormat':
        """Lookup a TimestampFormat from string specification."""
        if isinstance(spec, cls):
            return spec
        for timestamp_format in cls:
            if timestamp_format._spec_matcher.match(spec):
                return timestamp_format
        raise ValueError(f'Invalid timestamp format specification: {spec}')

    @staticmethod
    def _parse_tz(tz: Any = None) -> tzinfo:
        if isinstance(tz, tzinfo):
            return tz
        if tz:
            return pytz.timezone(tz)
        return pytz.UTC

    def parser(self, tz: Any = None) -> Callable[[Any], pd.Timestamp]:
        """Get a parser that uses a (default) timezone while parsing."""
        parser = self._parse[0]
        if not self._timezone_dependent:
            return parser

        timezone = self._parse_tz(tz)

        def _parse_with_tz(value: Any) -> pd.Timestamp:
            ts = parser(value)
            if not ts.tzinfo:
                ts = ts.replace(tzinfo=timezone)
            return ts.astimezone(pytz.UTC)
        return _parse_with_tz

    def formatter(self, tz: Any = None) -> Callable[[pd.Timestamp], Any]:
        """Get a formatter that uses a (default) timezone when relevant."""
        formatter = self._format[0]
        if not self._timezone_dependent:
            return formatter

        timezone = self._parse_tz(tz)
        return lambda ts: formatter(ts.astimezone(timezone))

    def __str__(self):
        """Get the string representation."""
        return self.value


@dataclass
class SeriesSettings:
    """Settings for the mapping of an input (import) or CSV output (export).

    Attributes:
        metric_column:
            The input attribute containing the metric id.
            This is a column name, or a pandas multiindex level name for the columns.
            If not specified:
            * if a `value_column` is specified, the default "metric" column is uses if present.
            * else, each column name (except the `resource_column` and `timestamp_column` ones),
                is a metric key and provide seperate series.
        metric:
            A default metric name for this import.
        metrics:
            A list of either:
            - metric keys retained from the input
            - `waylay.service.timeseries.parser.model.Metric` entries that describe and map metrics
            If specified, only series for these metrics are processed.
        resource_column:
            The input key containing the resource id.
            This is a column name, or a pandas multiindex level name for the columns.
            If not specified, a fixed `resource` should be specified,
            or the column key "resource" is used if present.
        resource:
            A default resource id to use for this import.
        resources:
            A list of either:
            - resource keys retained from the input
            - `waylay.service.timeseries.parser.model.Resource`
                entries that describe and map resources
            If specified, only series for these resources are processed.
        value_column:
            The column key containing the value. When set, the metric names should be
            provided through `metric` or `metric_column` (default "metric").
        timestamp_column:
            The input key containing the timestamp.
        timestamp_offset:
            A time interval to add to the input timestamp.
        timestamp_first:
            Forces the first timestamp, and increments
            the following timestamps with the same amount.
        timestamp_last:
            Forces the last timestamp, and increments the preceding timestamps with the same amount.
        timestamp_interval:
            Ignores the input timestamps and writes data with fixed timestamp intervals.
            Requires `timestamp_first`.
        timestamp_constructor:
            A callable that creates a `datetime` or `pandas.Timestamp` from the timestamp input.
        timestamp_timezone:
            A timezone indicator that should be used to interpret local time data.
        timestamp_from:
            Filters to have a timestamp equal to or greater than this one.
        timestamp_until:
            Filters to have a timestamp strictly less than this one.
    """

    metrics: Optional[Sequence[Union[str, Metric]]] = None
    metric_column: Optional[str] = None
    metric: Optional[str] = None

    resources: Optional[Sequence[Union[str, Resource]]] = None
    resource_column: Optional[str] = None
    resource: Optional[str] = None

    value_column: Optional[str] = None

    timestamp_column: Optional[str] = None
    timestamp_offset: Optional[timedelta] = None
    timestamp_first: Optional[datetime] = None
    timestamp_last: Optional[datetime] = None
    timestamp_interval: Optional[timedelta] = None
    timestamp_constructor: Optional[Callable[[Any], datetime]] = None
    timestamp_timezone: Optional[str] = None

    # TODO: document, review
    name: Optional[str] = None
    timestamp_from: Optional[Any] = None
    timestamp_until: Optional[Any] = None
    timestamp_formatter: Optional[Callable[[datetime], Any]] = None
    timestamp_format: Optional[TimestampFormat] = None
    write_csv_header: bool = True
    per_resource: bool = False
    per_metric: bool = False
    skip_empty_values = True

    def __post_init__(self):
        """Parse string input args to objects."""
        self.timestamp_format = (
            TimestampFormat.lookup(self.timestamp_format) if self.timestamp_format else None
        )
        self.timestamp_offset = parse_interval(self.timestamp_offset)
        self.timestamp_interval = parse_interval(self.timestamp_interval)

    def iter_metrics(self) -> Iterator[Metric]:
        """Iterate the metric specifications if available."""
        if not self.metrics:
            if self.metric:
                yield Metric(name=self.metric)
            return

        for metric in self.metrics:
            if isinstance(metric, Metric):
                metric_spec = metric
            else:
                metric_spec = Metric(name=metric)
            if self.metric and metric_spec.name != self.metric:
                continue
            yield metric_spec

    def iter_resources(self) -> Iterator[Resource]:
        """Iterate the resource specifications if available."""
        if not self.resources:
            if self.resource:
                yield Resource(id=self.resource)
            return

        for resource in self.resources:
            if isinstance(resource, Resource):
                resource_spec = resource
            else:
                resource_spec = Resource(id=resource)
            if self.resource and resource_spec.id != self.resource:
                continue
            yield resource_spec

    def metric_by_key(self, key: Optional[str]) -> Optional[str]:
        """Lookup the actual metric name for the given column key."""
        if not key:
            return self.metric
        if not self.metrics:
            return _remove_prefix(key)
        for metric in self.iter_metrics():
            if _remove_prefix(key) == (_remove_prefix(metric.key) or metric.name):
                return metric.name
        return None

    def key_by_metric(self, name: str) -> Optional[str]:
        """Lookup the column key that is used to represent the a given metric name.

        The empty key resolves to the default metric.
        """
        if not self.metrics:
            return name or self.metric
        for metric in self.iter_metrics():
            if name == metric.name:
                return metric.key or metric.name
        return self.metric

    def resource_by_key(self, key: Optional[str]) -> Optional[str]:
        """Lookup the actual resource id for the given resource key.

        The empty key resolves to the default resource.
        """
        if not key:
            return self.resource
        if not self.resources:
            return key
        for resource in self.iter_resources():
            if key == resource.key_or_id:
                return resource.id
        return self.resource

    def key_by_resource(self, resource_id: str) -> Optional[str]:
        """Lookup the column key that is used to represent the a given resource id."""
        if not self.resources:
            return resource_id
        for resource in self.iter_resources():
            if resource_id == resource.id:
                return resource.key_or_id
        return None

    def has_timestamp(self) -> bool:
        """Check wether the dataset should deliver timestamps."""
        return (
            self.timestamp_column is not None or
            self.timestamp_interval is None or (
                self.timestamp_first is None and
                self.timestamp_last is None
            )
        )

    def metric_for(self, metric_name: str) -> Metric:
        """Create a metadata object for the given metric names.

        Uses the `metrics` registered on this object as a data description catalog.
        """
        return next(
            (m for m in self.iter_metrics() if m.name == metric_name),
            Metric(metric_name)
        )

    def resource_for(
        self, resource_id: str,
        metric_names: Optional[Sequence[str]] = None
    ) -> Resource:
        """Create a metadata object for the given resource id and metric names.

        Uses the `resources` and `metrics` registered on this object as a data
        description catalog to enhance the _resource_ and _metric_
        references found in a concrete series.
        """
        resource_meta = next(
            (r for r in self.iter_resources() if r.id == resource_id),
            Resource(resource_id)
        )
        if metric_names is not None:
            resource_meta = resource_meta.with_metrics(
                list(
                    self.metric_for(metric_name)
                    for metric_name in metric_names
                )
            )
        return resource_meta

    def get_timestamp_formatter(self) -> Callable[[datetime], Any]:
        """Get the formatter for timestamps in csv exports."""
        if self.timestamp_formatter:
            return self.timestamp_formatter
        if self.timestamp_format:
            return self.timestamp_format.formatter(self.timestamp_timezone)
        return TimestampFormat.ISO.formatter(self.timestamp_timezone)

    def get_timestamp_parser(self, example: Any = None) -> Callable[[Any], datetime]:
        """Get the parser for timestamps in csv imports."""
        if self.timestamp_constructor:
            return self.timestamp_constructor
        if self.timestamp_format:
            return self.timestamp_format.parser(self.timestamp_timezone)

        if example:
            try:
                return _detect_timestamp_unix_unit(example).parser()
            except (ValueError, TypeError):
                example_ts = TimestampFormat.ISO.parser(self.timestamp_timezone)(example)
                return TimestampFormat.ISO.parser(self.timestamp_timezone or example_ts.tzinfo)

        return TimestampFormat.AUTO.parser(self.timestamp_timezone)

    def parse_timestamp(self, value: Any) -> Optional[datetime]:
        """Parse a timestamp, fall back to ISO."""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return self.get_timestamp_parser()(value)
        except ValueError:
            return TimestampFormat.ISO.parser(self.timestamp_timezone)(value)

    def get_timestamp_from(self) -> Optional[datetime]:
        """Get the from timestamp, if any."""
        return self.parse_timestamp(self.timestamp_from)

    def get_timestamp_until(self) -> Optional[datetime]:
        """Get the until timestamp, if any."""
        return self.parse_timestamp(self.timestamp_until)


def _remove_prefix(metric_key: Optional[str]) -> Optional[str]:
    if metric_key and metric_key.startswith(METRIC_PREFIX):
        return metric_key[METRIC_PREFIX_LENGTH:]
    return metric_key


@dataclass
class ETLFile:
    """Defines a local ETL export/import file and workspace.

    Attributes:
        directory:
            The (local) directory used to store the ETL file and associated temporary files.
        prefix:
            The prefix used to create the ETL file. If not specified
            is defaulted to `import-{current timestamp}`.
    """

    directory: Optional[PathLike] = None
    prefix: Optional[str] = None

    def __post_init__(self):
        """Compute default prefix if not given as constructor parameter."""
        if not self.prefix:
            self.prefix = f'import-{datetime.utcnow():%Y%m%d.%H%M%S}'
        if not self.directory:
            self.directory = tempfile.mkdtemp(prefix='etl-import')

    @property
    def name(self) -> str:
        """Get the name of the ETL file."""
        return f'{self.prefix}-timeseries.csv.gz'

    @property
    def path(self) -> Path:
        """Get the full path of the ETL file."""
        assert self.directory is not None  # see __post_init__
        return Path(self.directory) / self.name


SeriesInput = Union[
    ETLFile,
    pd.DataFrame,
    str,
    os.PathLike,
    io.TextIOBase,
    Iterable[str],
    Iterable[Sequence[str]],
]


@dataclass
class WaylayETLSeriesImport:
    """A (reference to) a local file in the waylay ETL timeseries format and associated metadata."""

    series_input: Sequence[SeriesInput] = field(repr=False)
    import_file: ETLFile
    settings: SeriesSettings
    storage_bucket: str = ETL_IMPORT_BUCKET

    @property
    def storage_object_name(self):
        """Get default upload storage location."""
        return f'{ETL_IMPORT_UPLOAD_PREFIX}{self.import_file.name}'

    @property
    def name(self):
        """Get the name that identifies the import."""
        return self.import_file.prefix


@runtime_checkable
class CSVWriteable(Protocol):
    """Aything that can receive string writes."""

    def write(self, _: str) -> Any:
        """Write a string."""


CSVOutput = Union[
    str,
    os.PathLike,
    IO,
    CSVWriteable,
    ZipFile,
    TarFile
]


class ArchiveType(str, Enum):
    """Typed enumeration of supported archive import and export types."""

    description: str
    supports_multiple_files: bool
    expected_suffixes: List[str]
    excluded_suffixes: List[str]
    is_dir_type: bool

    def __new__(
        cls,
        value: str,
        description: str,
        supports_multiple_files: bool,
        expected_suffixes: Optional[List[str]] = None,
        excluded_suffixes: Optional[List[str]] = None,
        is_dir_type: bool = False,
    ):
        """Construct an enum value.

        See https://docs.python.org/3/library/enum.html#when-to-use-new-vs-init.
        """
        obj = str.__new__(cls, value)
        obj._value_ = value
        obj.description = description
        obj.supports_multiple_files = supports_multiple_files
        obj.expected_suffixes = expected_suffixes or []
        obj.excluded_suffixes = excluded_suffixes or []
        obj.is_dir_type = is_dir_type
        return obj

    TEXT = ('text', 'Single csv text file.', False, ['.csv'], ['.zip', '.tar', '.gz'])
    DIR = ('dir', 'Directory with csv text files.', True, None, None, True)
    DIR_GZ = ('dirgz', 'Directory with compressed csv text files.', True, None, None, True)
    ZIP = ('zip', 'Zip archive of csv text files.', True, ['.zip'])
    GZ = ('gz', 'Single compressed csv text file.', False, ['.gz'], ['.tar'])
    TAR = ('tar', 'Tar archive of csv text files.', True, ['.tar'], ['.gz'])
    TAR_GZ = ('targz', 'Compressed Tar archive of csv text files.', True, ['.tar', '.gz'])

    def __str__(self):
        """Get the string representation."""
        return self.value

    @classmethod
    def lookup(cls, value: Optional[str]) -> Optional['ArchiveType']:
        """Lookup an enum object from a str value."""
        if value is None:
            return None
        # workaround for lint and typing issues with replaced __new__ for enums
        # pylint: disable=no-value-for-parameter
        return ArchiveType(value.lower().replace('.', ''))  # type: ignore

    @classmethod
    def supported_for(cls, path: Path, multiple_files: bool) -> List['ArchiveType']:
        """Return a list of supported archive types, given a path and multiple_files flag."""
        if path.exists() and path.is_dir():
            return [
                at for at in list(ArchiveType)
                if at.is_dir_type
            ]
        archive_types_for_path = [
            at
            for at in list(ArchiveType)
            if at.expected_suffixes
            if all(s in path.suffixes for s in at.expected_suffixes)
            if not any(s in path.suffixes for s in at.excluded_suffixes)
        ]
        return [
            at for at in (archive_types_for_path or list(ArchiveType))
            if not multiple_files or at.supports_multiple_files
        ]

    @classmethod
    def for_import(cls, path: Path) -> Optional['ArchiveType']:
        """Return the archive type for import, as inferred from an existing file name."""
        if path.exists() and path.is_dir():
            return ArchiveType.DIR
        if path.suffixes and path.suffixes[-1] == '.tgz':
            return ArchiveType.TAR_GZ
        return next((
            at for at in list(ArchiveType)
            if at.expected_suffixes
            if all(s in path.suffixes for s in at.expected_suffixes)
            if not any(s in path.suffixes for s in at.excluded_suffixes)
        ), ArchiveType.TEXT)
