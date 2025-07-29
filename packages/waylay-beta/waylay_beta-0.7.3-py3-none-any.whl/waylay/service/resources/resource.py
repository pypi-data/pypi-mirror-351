"""REST definitions for the resource entity of the api service."""

from waylay.service import WaylayResource
from waylay.service import decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]

RESOURCE_ID_ARG = {
    'name': 'resource_id',
    'type': 'str',
    'description': 'id of a Waylay resource.',
    'example': 'my_custom_sensor_001.a8b230ff'
}
RESOURCE_BODY_ARG = {
    'name': 'body',
    'type': 'dict',
    'description': 'Representation of a resource entity',
    'examples': ["""{
            "name" : "a demo custom sensor",
            "id": "my_custom_sensor_001.a8b230ff",
            "resourceTypeId": "CustomSensor001",
            "parentId": "demoroom_001",
        }"""]
}
ADDITIONAL_PARAMS_ARG = {
    'name': 'params',
    'type': 'dict',
    'description': 'Additional parameters, mapped to url query parameters. See API documentation.'
}


class ResourceResource(WaylayResource):
    """REST Resource for the `resource` entity of the `api` (resource provisioning) service."""

    link_roots = {
        'doc': '${doc_url}/api/resources/?id=',
        'apidoc': '${apidoc_url}/resources.html'
    }

    actions = {
        'get': {
            'method': 'GET',
            'url': '/resources/{}',
            'arguments': [RESOURCE_ID_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Retrieve a `resource` representation.',
            'links': {
                'doc': 'retrieve-resource',
                'apidoc': '',
            },
        },
        'create': {
            'method': 'POST',
            'url': '/resources',
            'arguments': [RESOURCE_BODY_ARG],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator(['entity'])
            ],
            'description': 'Create a `resource` entity.',
            'links': {
                'doc': 'create-resource',
                'apidoc': '',
            },
        },
        'update': {
            'method': 'PATCH',
            'url': '/resources/{}',
            'arguments': [RESOURCE_ID_ARG, RESOURCE_BODY_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': '(Partially) update a `resource` representation.',
            'links': {
                'doc': 'partial-resource-update',
                'apidoc': '',
            },
        },
        'replace': {
            'method': 'PUT',
            'url': '/resources/{}',
            'arguments': [RESOURCE_ID_ARG, RESOURCE_BODY_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Replace a `resource` representation.',
            'links': {
                'doc': 'update-resource',
                'apidoc': '',
            },
        },
        'remove': {
            'method': 'DELETE',
            'url': '/resources/{}',
            'arguments': [RESOURCE_ID_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Delete a `resource` entity.',
            'links': {
                'doc': 'delete-resource',
                'apidoc': '',
            },
        },
        'list': {
            'method': 'GET',
            'url': '/resources',
            'arguments': [ADDITIONAL_PARAMS_ARG],
            'decorators': [
                decorators.exception_decorator,
                decorators.return_path_decorator(['values'])
            ],
            'description': 'Query `resource` entities.',
            'links': {
                'doc': 'query-resources',
                'apidoc': '',
            },
        },
    }
