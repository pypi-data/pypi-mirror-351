"""REST definitions for version status of Waylay Storage service."""
from urllib.parse import quote
from waylay.service import WaylayResource, decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]


class AboutResource(WaylayResource):
    """Static information about version."""

    link_roots = {
        'doc': '${doc_url}/api/storage/?id=',
        'apidoc': '${apidoc_url}/storage.html'
    }

    actions = {
        'version': {
            'method': 'GET',
            'url': '/',
            'decorators': DEFAULT_DECORATORS,
            'description': 'Application version',
            'links': {
                'doc': 'version',
                'apidoc': '',
            },
        },
        'status': {
            'method': 'GET',
            'url': '/status',
            'decorators': DEFAULT_DECORATORS,
            'description': 'Validation and statistics on the buckets and policies for this tenant.',
            'links': {
                'doc': 'tenant-status',
                'apidoc': '',
            },
        },
    }
