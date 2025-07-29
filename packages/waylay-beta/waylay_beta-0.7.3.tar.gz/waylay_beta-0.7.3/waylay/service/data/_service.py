
"""REST client for the Waylay Data Service (broker)."""

from waylay.service import WaylayRESTService

from .series import SeriesResource
from .events import EventsResource


class DataService(WaylayRESTService):
    """REST client for the Waylay Data Service (broker)."""

    config_key = 'data'
    service_key = 'data'
    gateway_root_path = '/data/v1'
    resource_definitions = {
        'series': SeriesResource,
        'events': EventsResource,
    }

    series: SeriesResource
    events: EventsResource
