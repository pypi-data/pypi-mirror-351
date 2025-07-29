"""REST definitions for the 'series' entity of the 'data' service."""
from typing import Any, Dict, Iterator, Tuple, Optional

import urllib.parse

from waylay.service import WaylayResource
from waylay.service import decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]
DEFAULT_EXPORT_PAGE_SIZE = 2000


RESOURCE_ARG = {
    'name': 'resource_id',
    'type': 'str',
    'description': 'The id of a waylay resource.'
}
METRIC_ARG = {
    'name': 'metric',
    'type': 'str',
    'description': 'The name of the metric of a resource series.'
}
ADDITIONAL_PARAMS_ARG = {
    'name': 'params',
    'type': 'dict',
    'description': 'Additional parameters, mapped to url query parameters. See API documentation.'
}


class SeriesResource(WaylayResource):
    """REST Resource for the 'series' entity of the 'data' service."""

    link_roots = {
        'doc': '${doc_url}/api/broker/?id=',
        'apidoc': '${apidoc_url}/broker.html'
    }

    actions = {
        'data': {
            'method': 'GET', 'url': '/series/{}/{}',
            'arguments': [
                RESOURCE_ARG, METRIC_ARG, ADDITIONAL_PARAMS_ARG
            ],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator(['series']),
            ],
            'description': 'Retrieve the (optionally aggregated) data of a single series.',
            'links': {
                'doc':  'getting-time-series-data'
            },
        },
        'list': {
            'method': 'GET', 'url': '/series/{}',
            'arguments': [RESOURCE_ARG, ADDITIONAL_PARAMS_ARG],
            'decorators': [
                decorators.default_params_decorator({'metadata': 'true'}),
                decorators.exception_decorator,
                decorators.return_path_decorator([]),
            ],
            'description': 'Retrieve a list of series and their latest value for a given resource.',
            'links': {
                'doc': 'metadata',
                'apidoc': '',
            },
        },
        'latest': {
            'method': 'GET', 'url': '/series/{}/{}/latest',
            'arguments': [RESOURCE_ARG, METRIC_ARG],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator([])
            ],
            'description': 'Fetch the latest value for a series.',
            'links': {
                'doc': 'latest-value-for-a-series',
                'apidoc': '',
            },
        },
        'query': {
            'method': 'POST', 'url': '/series/query',
            'arguments': [{
                'name': 'body',
                'type': 'Dict',
                'description': 'A series query specification (see REST API doc).'
            }],
            'description': 'Execute a broker query document to retrieve aggregated timeseries.',
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator(['series'])
            ],
            'links': {
                'doc': 'post-timeseries-query',
                'apidoc': '',
            },
        },
        'export': {
            'method': 'GET',
            'url': '/series/{}/{}/raw',
            'arguments': [RESOURCE_ARG, METRIC_ARG, ADDITIONAL_PARAMS_ARG],
            'description': 'Export a single series using paging with HAL links.',
            'decorators': [
                decorators.exception_decorator,
                decorators.default_params_decorator(
                    {'from': 0, 'limit': DEFAULT_EXPORT_PAGE_SIZE, 'order': 'ascending'}),
                decorators.default_header_decorator({'Accept': 'application/hal+json'}),
                decorators.return_path_decorator(['series']),
            ],
            'links': {
                'doc': 'getting-time-series-data',
                'apidoc': '',
            },
        }
    }

    def iter_export(
        self, resource_id: str, metric: str,
        page_size: Optional[int] = None,
        descending: bool = False,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Iterator[Tuple[int, Any]]:
        """Fully export a timeseries.

        Uses paging on the '/series/{}/{}/raw' endpoint.

        Parameters
            resource_id: the resource id for the timeseries
            metric: the metric of the timeseries
            page_size: the `limit` size with which data is retrieved using the `export` action
            descending: if true, the series is iterated descending (`order=descending`)
            params: URL params that are passed to the `export` action. These might include:
                params.from: export start timestamp
                params.until: export end timestamp
            kwargs: other params are passed onto the `export` action
        """
        export_params = params or {}
        export_params['limit'] = page_size
        if descending:
            export_params['order'] = 'descending'
        if kwargs.pop('select_path', None):
            raise AttributeError('Cannot specify `select_path` in `iter_export`')
        while True:
            resp = self.export(  # pylint: disable=no-member
                resource_id, metric,
                select_path=None, params=export_params, **kwargs
            )
            if 'series' in resp:
                yield from resp['series']
            next_link = resp.get('_links', {}).get('next', {}).get('href')
            if not next_link:
                return
            next_query = urllib.parse.urlparse(next_link).query
            export_params = urllib.parse.parse_qs(next_query)
