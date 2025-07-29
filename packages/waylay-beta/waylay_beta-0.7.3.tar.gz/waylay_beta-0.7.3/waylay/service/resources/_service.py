"""REST client for the Waylay Resources API Service."""

from waylay.service import WaylayRESTService

from .resource import ResourceResource
from .resource_type import ResourceTypeResource


class ResourcesService(WaylayRESTService):
    """REST client for the main Waylay Resources Service."""

    config_key = 'resources'
    service_key = 'resources'
    gateway_root_path = '/resources/v1'
    resource_definitions = {
        'resource': ResourceResource,
        'resource_type': ResourceTypeResource
    }
    resource: ResourceResource
    resource_type: ResourceTypeResource
