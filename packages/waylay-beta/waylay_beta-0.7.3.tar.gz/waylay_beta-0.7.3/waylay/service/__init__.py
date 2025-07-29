"""Waylay Rest Services."""

from ._base import WaylayRESTService, WaylayResource, WaylayServiceContext, WaylayService, WaylayAction
from . import _decorators as decorators

from .byoml import ByomlService
from .timeseries import TimeSeriesService
from .resources import ResourcesService
from .storage import StorageService
from .util import UtilService
from .etl import ETLService
from .data import DataService
from .queries import QueriesService


SERVICES = [
    ByomlService,
    TimeSeriesService,
    QueriesService,
    ResourcesService,
    StorageService,
    UtilService,
    ETLService,
    DataService
]
