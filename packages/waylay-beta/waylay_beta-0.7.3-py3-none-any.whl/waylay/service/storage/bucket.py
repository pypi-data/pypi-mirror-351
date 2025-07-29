"""REST definitions for the 'bucket' entity of the 'storage' service."""
from urllib.parse import quote

from waylay.service import WaylayResource, decorators

BUCKET_NAME_ARG = {
    'name': 'bucket_name',
    'type': 'str',
    'description': 'Name of a Waylay storage bucket.',
    'examples': ['assets', 'public']
}
ADDITIONAL_PARAMS_ARG = {
    'name': 'params',
    'type': 'dict',
    'description': 'Additional parameters, mapped to url query parameters. See API documentation.'
}


class BucketResource(WaylayResource):
    """REST Resource for the 'bucket' entity of the 'storage' service."""

    link_roots = {
        'doc': '${doc_url}/api/storage/?id=',
        'apidoc': '${apidoc_url}/storage.html'
    }

    actions = {
        'list': {
            'method': 'GET', 'url': '/bucket', 'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator(['buckets']),
            ],
            'description': 'List available bucket aliases',
            'links': {
                'doc': 'list-bucket',
                'apidoc': '',
            }
        },
        'get': {
            'method': 'GET', 'url': '/bucket/{}', 'decorators': [
                decorators.exception_decorator,
                decorators.return_body_decorator,
            ],
            'arguments': [BUCKET_NAME_ARG],
            'description': 'Get metadata for a specific bucket alias',
            'links': {
                'doc': 'get-bucket',
                'apidoc': '',
            }
        },
    }
