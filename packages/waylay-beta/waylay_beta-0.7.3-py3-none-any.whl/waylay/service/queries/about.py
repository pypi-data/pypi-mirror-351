"""REST definitions for version status of Waylay Queries Service."""

from .._base import WaylayResource
from .._decorators import (
    exception_decorator,
    return_path_decorator
)


class AboutResource(WaylayResource):
    """Version information."""

    actions = {
        'version': {
            'method': 'GET',
            'url': '/',
            'decorators': [exception_decorator, return_path_decorator(['version'])],
            'description': 'Version info of the <em>Queries Service</em> at this endpoint.'
        }
    }
