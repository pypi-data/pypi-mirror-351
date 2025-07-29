"""REST definitions for the 'runtime' entity of the 'byoml' service."""
from typing import (
    Optional, Dict
)
from .._base import WaylayResource
from .._decorators import (
    return_body_decorator,
    return_path_decorator,
)
from ._decorators import (
    byoml_exception_decorator,
    byoml_retry_decorator,
)

FRAMEWORK_ARG = {
    'name': 'framework',
    'type': 'str',
    'description': 'Byoml framework name for a supported runtime.',
    'examples': ['sklearn', 'custom']
}
FRAMEWORK_VERSION_ARG = {
    'name': 'framework_version',
    'type': 'str',
    'description': (
        'Framework version specifier. '
        'Supports (python version specifiers)[https://packaging.pypa.io/en/latest/specifiers.html]'
    ),
    'examples': ['2.1', '>=2.1,<2.4']
}
FRAMEWORK_LIST_RETURN = {
    'name': 'frameworks',
    'type': 'List[Dict]',
    'description': 'Representation of supported frameworks.'
}


class FrameworkResource(WaylayResource):
    """REST Inspect supported runtimes for a given framework."""

    link_roots = {
        'doc': '${doc_url}/api/byoml/?id=',
        'apidoc': '${apidoc_url}/byoml.html'
    }

    actions = {
        'list': {
            'method': 'GET',
            'url': '/frameworks',
            'returns': [
                FRAMEWORK_LIST_RETURN
            ],
            'decorators': [
                byoml_exception_decorator,
                return_path_decorator(['frameworks'])
            ],
            'description': 'Frameworks and supported runtimes.',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        },
        'get': {
            'method': 'GET',
            'url': '/frameworks/{}',
            'arguments': [FRAMEWORK_ARG],
            'decorators': [
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': 'Get the default runtime for a framework.',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        },
        'list_versions': {
            'method': 'GET',
            'url': '/frameworks/{}/versions',
            'arguments': [FRAMEWORK_ARG],
            'decorators': [
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': 'Get the runtimes for a framework.',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        },
        'get_version': {
            'method': 'GET',
            'url': '/frameworks/{}/versions/{}',
            'arguments': [FRAMEWORK_ARG, FRAMEWORK_VERSION_ARG],
            'decorators': [
                byoml_exception_decorator,
                byoml_retry_decorator,
                return_body_decorator,
            ],
            'description': 'Get the runtime for a given framework and framework version.',
            'links': {
                'doc': 'runtimes',
                'apidoc': '',
            },
        }
    }

    def find_runtime(self, framework: str, framework_version: Optional[str]) -> Dict:
        """Get the byoml plug runtime for this framework and version (default version if not specified).

        framework: the name of the framework
        framework_version: (optional) the version for this framework, the default version is defined by
                           the byoml service itself.
        """
        if framework_version:
            return self.get_version(framework, framework_version)  # pylint: disable=no-member
        return self.get(framework)['default_runtime']  # pylint: disable=no-member
