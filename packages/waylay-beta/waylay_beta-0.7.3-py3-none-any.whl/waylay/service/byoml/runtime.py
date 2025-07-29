"""REST definitions for the 'runtime' entity of the 'byoml' service."""

from .._base import WaylayResource
from .._decorators import (
    return_body_decorator,
    return_path_decorator,
)
from ._decorators import (
    byoml_exception_decorator,
    byoml_retry_decorator,
)


RUNTIME_ARG = {
    'name': 'runtime',
    'type': 'str',
    'description': 'Name of a supported Byoml runtime.',
    'examples': ['byoml-sklearn-0.24']
}
RUNTIME_RETURN = {
    'name': 'runtime',
    'type': 'Dict',
    'description': 'Representation of a supported runtime.'
}
RUNTIME_LIST_RETURN = {
    'name': 'runtimes',
    'type': 'List[Dict]',
    'description': 'Representation of supported runtimes.'
}


class RuntimeResource(WaylayResource):
    """REST Resource for the 'runtime' entity of the 'byoml' service."""

    link_roots = {
        'doc': '${doc_url}/api/byoml/?id=',
        'apidoc': '${apidoc_url}/byoml.html'
    }

    actions = {
        'list': {
            'method': 'GET',
            'url': '/runtimes',
            'returns': [RUNTIME_LIST_RETURN],
            'decorators': [
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_path_decorator(['runtimes'])
            ],
            'description': 'List runtimes (framework and framework version).',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        },
        'get': {
            'method': 'GET',
            'url': '/runtimes/{}',
            'arguments': [RUNTIME_ARG],
            'returns': [RUNTIME_RETURN],
            'decorators': [
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': 'Get a supported runtime.',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        }
    }
