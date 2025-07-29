
"""REST client for the Waylay Byoml Service."""

from .._base import WaylayRESTService

from .model import ModelResource
from .runtime import RuntimeResource
from .framework import FrameworkResource
from .about import AboutResource


class ByomlService(WaylayRESTService):
    """REST client for the Waylay BYOML Service."""

    service_key = 'byoml'
    config_key = 'byoml'
    gateway_root_path = '/ml/v1'

    resource_definitions = {
        'model': ModelResource,
        'about': AboutResource,
        'framework': FrameworkResource,
        'runtime': RuntimeResource
    }

    model: ModelResource
    runtime: RuntimeResource
    framework: FrameworkResource
    about: AboutResource
