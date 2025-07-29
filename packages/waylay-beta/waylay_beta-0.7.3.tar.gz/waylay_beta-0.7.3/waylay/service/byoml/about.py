"""REST definitions for status of Waylay BYOML service."""

from .._base import WaylayResource
from .._decorators import (
    exception_decorator,
    return_body_decorator
)

DEFAULT_DECORATORS = [exception_decorator, return_body_decorator]


class AboutResource(WaylayResource):
    """Static status endpoint."""

    actions = {
        'health': {
            'method': 'GET',
            'url': '/',
            'decorators': DEFAULT_DECORATORS,
            'description': 'Get the health status of the <em>BYOML Service</em>'
        }
    }
