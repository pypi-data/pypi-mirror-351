"""REST definitions for the 'series' entity of the 'data' service."""

from waylay.service import WaylayResource
from waylay.service import decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]

RESOURCE_ARG = {
    'name': 'resource_id',
    'type': 'str',
    'description': 'The id of a waylay resource.'
}


class EventsResource(WaylayResource):
    """REST Resource for the 'events' ingestion of the 'data' service."""

    link_roots = {
        'doc': '${doc_url}/api/broker/?id=',
        'apidoc': '${apidoc_url}/broker.html'
    }

    actions = {
        'post': {
            'method': 'POST', 'url': '/events/{}',
            'arguments': [RESOURCE_ARG],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator([]),
            ],
            'description': (
                'Forward a json message to the rule engine, '
                'time series database and/or document store for a given resource.'
            ),
            'links': {
                'doc': 'posting-data-to-the-storage-and-rule-engine',
                'apidoc': '',
            },
        },
        'bulk': {
            'method': 'POST', 'url': '/events',
            'returns': [
            ],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator([])
            ],
            'description': (
                'Forward an array of json messages to the rule engine, '
                'time series database and/or document store.'
            ),
            'links': {
                'doc': 'posting-array-of-data',
                'apidoc': '',
            },
        },
        'remove': {
            'method': 'DELETE', 'url': '/{}',
            'arguments': [RESOURCE_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Remove all data for a resource.',
            'links': {
                'doc': 'all-data-for-a-resource',
                'apidoc': '',
            },
        },
    }

    def get_action_full_url(self, action_name, *parts):
        """Override the regular url computation when not using api gateway."""
        via_gateway = '/data/v1' in self.api_root_url
        if not via_gateway and action_name == 'remove':
            # remove not via api:
            return self.api_root_url + f'resources/{parts[0]}'
        else:
            return super().get_action_full_url(action_name, *parts)
