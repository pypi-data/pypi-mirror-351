"""Definitions for the 'query' entity of the 'queries' Service."""
from typing import Union, Dict

from .._base import WaylayResource
from .._decorators import (
    return_path_decorator
)
from ._decorators import (
    query_exception_decorator,
    query_return_dataframe_decorator,
    MultiFrameHandling,
)
from ._exceptions import (
    QueryRequestError, RestResponseError
)


CONFIG_ENTITY_DECORATORS = [
    query_exception_decorator,
    return_path_decorator(['query'])
]

CONFIG_LIST_DECORATORS = [
    query_exception_decorator,
    return_path_decorator(['queries', 'name'])
]

DATA_RESPONSE_DECORATORS = [
    query_exception_decorator,
    query_return_dataframe_decorator(
        'data',
        default_frames_handling=MultiFrameHandling.JOIN
    )
]

CONFIG_STATUS_DECORATORS = [
    query_exception_decorator,
    return_path_decorator([])
]

QUERY_NAME_ARG = {
    'name': 'name',
    'type': 'str',
    'description': 'Name for stored query.',
    'example': 'my_query_001'
}
QUERY_ENTITY_BODY = {
    'name': 'body',
    'type': 'dict',
    'description': 'A representation of a query entity.',
    'examples': ["""{
            "name": "max_flow_099",
            "query": {
                "freq": "PT1H",
                "aggregation": "max",
                "resource": "device_099",
                "data": [{ "metric": "flow"}]
            },
            "meta": { "description": "demo query" }
        }"""]
}
QUERY_DEFINITION_BODY = {
    'name': 'body',
    'type': 'dict',
    'description': 'A query definition.',
    'examples': ["""{
            "freq": "PT1H",
            "aggregation": "max",
            "resource": "device_099",
            "data": [{ "metric": "flow"}]
        }"""]
}
QUERY_ENTITY_OR_DEFINITION_BODY = {
    'name': 'body',
    'type': 'dict',
    'description': (
        'A representation of a query entity (including metadata), '
        'or the query definition itself.'
    ),
    'examples': [
        """{
            "name": "max_flow_099",
            "query": {
                "freq": "PT1H",
                "aggregation": "max",
                "resource": "device_099",
                "data": [{ "metric": "flow"}]
            },
            "meta": { "description": "demo query" }
        }""",
        """{
            "freq": "PT1H",
            "aggregation": "max",
            "resource": "device_099",
            "data": [{ "metric": "flow"}]
        }""",
    ]
}
QUERY_ENTITY_RESULT = {
    'name': 'query_definition',
    'type': 'Dict',
    'description': 'A representation of the stored query.',
}
ADDITIONAL_PARAMS_ARG = {
    'name': 'params',
    'type': 'dict',
    'description': (
        'Additional parameters, mapped to url query parameters. See API documentation.'
    ),
}


class QueryResource(WaylayResource):
    """REST Resource for the 'query' entity of the 'queries' Service."""

    link_roots = {
        'doc': '${doc_url}/api/query/',
        'apidoc':  '${apidoc_url}/queries.html'
    }

    actions = {
        'list': {
            'method': 'GET',
            'url': '/query',
            'arguments': [ADDITIONAL_PARAMS_ARG],
            'returns': [{
                'name': 'query_names',
                'type': 'List[str]',
                'description': 'A list of query names'
            }],
            'decorators': CONFIG_LIST_DECORATORS,
            'description': (
                'List the names of stored queries. '
                '<br>Use filter like <code>params=dict(q="name:demo")</code> to filter the listing. '
                '<br>Use <code>select_path=["queries"]</code> to return the query entities rather than names. '
            ),
            'links': {
                'doc': '?id=data-query-search-api',
                'apidoc': '#/query%20config/get_config_query'
            }
        },
        'create': {
            'method': 'POST',
            'url': '/query',
            'arguments': [QUERY_ENTITY_BODY],
            'decorators': CONFIG_ENTITY_DECORATORS,
            'description': (
                'Store a new query definition under a name. '
                'Fails if a query already exist with that name.'
            ),
            'links': {
                'doc': '?id=create',
                'apidoc': '#/query%20config/post_config_query'
            }
        },
        'get': {
            'method': 'GET',
            'url': '/query/{}',
            'arguments': [QUERY_NAME_ARG],
            'decorators': CONFIG_ENTITY_DECORATORS,
            'description': 'Get the named query definition.',
            'links': {
                'doc': '?id=retrieve',
                'apidoc': '#/query%20config/get_config_query__query_name_'
            }
        },
        'remove': {
            'method': 'DELETE',
            'url': '/query/{}',
            'arguments': [QUERY_NAME_ARG],
            'decorators': CONFIG_STATUS_DECORATORS,
            'description': 'Remove the named query definition.',
            'links': {
                'doc': '?id=delete',
                'apidoc': '#/query%20config/delete_config_query__query_name_'
            }
        },
        'replace': {
            'method': 'PUT',
            'url': '/query/{}',
            'arguments': [QUERY_NAME_ARG, QUERY_ENTITY_OR_DEFINITION_BODY],
            'decorators': CONFIG_ENTITY_DECORATORS,
            'description': 'Replace the named query defition.',
            'links': {
                'doc': '?id=replace',
                'apidoc': '#/query%20config/put_config_query__query_name_'
            }
        },
        '_execute_by_name': {
            'method': 'GET',
            'url': '/data/{}',
            'arguments': [QUERY_NAME_ARG, ADDITIONAL_PARAMS_ARG],
            'decorators': DATA_RESPONSE_DECORATORS,
            'description': (
                'Execute the timeseries query specified by the stored defintion of this name.'
            ),
            'links': {
                'doc': '?id=query-execution',
                'apidoc': '#/data/get_data_query__query_name_'
            }
        },
        '_execute_by_definition': {
            'method': 'POST',
            'url': '/data',
            'arguments': [QUERY_DEFINITION_BODY, ADDITIONAL_PARAMS_ARG],
            'decorators': DATA_RESPONSE_DECORATORS,
            'description': 'Execute the timeseries query specified in the request body.',
            'links': {
                'doc': '?id=query-execution',
                'apidoc': '#/data/post_data_query'
            }
        },
        'execute': {
            'arguments': [{
                'name': 'name_or_query',
                'type': 'Union[str, Dict]',
                'description': 'Either a name or query definition.'
            }, ADDITIONAL_PARAMS_ARG],
            'returns': [{
                'name': 'result',
                'type': 'pandas.DataFrame',
                'description': (
                    "A Pandas Dataframe containing the data, "
                    "unless 'response_constructor' specifies otherwise."
                )
            }],
            'wrapped_actions': ['_execute_by_name', '_execute_by_definition']
        },
        'create_or_replace': {
            'arguments': [
                {
                    'name': 'name',
                    'type': 'Optional[str]',
                    'description': 'Query name, if not given in body argument.'
                },
                QUERY_ENTITY_OR_DEFINITION_BODY,
                ADDITIONAL_PARAMS_ARG
            ],
            'wrapped_actions': ['create', 'replace']
        }
    }

    def execute(self, name_or_query: Union[str, Dict, None] = None, *, body: Dict = None, **kwargs):
        """Execute a timeseries query by name (string) or definition (object)."""
        if isinstance(name_or_query, str):
            return self._execute_by_name(name_or_query, **kwargs)  # pylint:disable=no-member

        # support query to be specified in the `body` argument
        query = name_or_query or body
        if isinstance(query, Dict):
            return self._execute_by_definition(body=query, **kwargs)  # pylint:disable=no-member

        raise QueryRequestError('The first argument should be a query name or definition.')

    def create_or_replace(
        self, name_or_query: Union[str, Dict, None] = None, *, body: Dict = None, **kwargs
    ):
        """Create or replace a query definition."""
        name = None
        if isinstance(name_or_query, str):
            name = name_or_query
        else:
            body = body or name_or_query
        if not body:
            raise QueryRequestError('Missing `body` argument with a query definition.')
        name = name or body.get('name')
        if not name:
            raise QueryRequestError(
                'Missing `name` as first argument or as property of the `body`.'
            )
        try:
            return self.replace(name, body=body, **kwargs)  # pylint:disable=no-member
        except RestResponseError as exc:
            if exc.response.status_code != 404:
                raise exc
            body = body if 'query' in body else dict(name=name, query=body)
            return self.create(body=body, **kwargs)  # pylint:disable=no-member
