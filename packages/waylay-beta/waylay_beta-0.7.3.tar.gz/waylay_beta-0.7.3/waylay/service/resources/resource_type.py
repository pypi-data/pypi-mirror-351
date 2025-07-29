"""REST definitions for the 'resource_type' entity of the 'api' service."""

from waylay.service import WaylayResource
from waylay.service import decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]

RESOURCE_TYPE_ID_ARG = {
    'name': 'resource_type_id',
    'type': 'str',
    'description': 'id of a Waylay resource type.',
    'example': 'CustomSensor001'
}
RESOURCE_TYPE_BODY_ARG = {
    'name': 'body',
    'type': 'dict',
    'description': 'Representation of a resource type entity',
    'examples': ["""{
            "name" : "CustomSensor001",
            "id": "dvtp_custom_sensor_001"
        }"""]
}
ADDITIONAL_PARAMS_ARG = {
    'name': 'params',
    'type': 'dict',
    'description': 'Additional parameters, mapped to url query parameters. See API documentation.'
}


class ResourceTypeResource(WaylayResource):
    """REST Resource for the 'resource_type' entity of the 'api' resource provisioning service."""

    link_roots = {
        'doc': '${doc_url}/api/resources/?id=',
        'apidoc': '${apidoc_url}/resources.html'
    }

    actions = {
        'create': {
            'method': 'POST',
            'url': '/resourcetypes',
            'arguments': [RESOURCE_TYPE_BODY_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Create a `resource type` entity.',
            'links': {
                'doc': 'create-resource-type',
                'apidoc': '',
            },
        },
        'remove': {
            'method': 'DELETE',
            'url': '/resourcetypes/{}',
            'arguments': [RESOURCE_TYPE_ID_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Delete a `resource type` entity.',
            'links': {
                'doc': 'delete-resource-type',
                'apidoc': '',
            },
        },
        'replace': {
            'method': 'PUT',
            'url': '/resourcetypes/{}',
            'arguments': [RESOURCE_TYPE_ID_ARG, RESOURCE_TYPE_BODY_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Replace a `resource type` representation.',
            'links': {
                'doc': 'update-resource-type',
                'apidoc': '',
            },
        },
        'update': {
            'method': 'PATCH',
            'url': '/resourcetypes/{}',
            'arguments': [RESOURCE_TYPE_ID_ARG, RESOURCE_TYPE_BODY_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': '(Partially) update a `resource type` representation.',
            'links': {
                'doc': 'partial-resource-type-update',
                'apidoc': '',
            },
        },
        'get': {
            'method': 'GET',
            'url': '/resourcetypes/{}',
            'arguments': [RESOURCE_TYPE_ID_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Retrieve a `resource type` representation.',
            'links': {
                'doc': 'retrieve-resource-type',
                'apidoc': '',
            },
        },
        'list': {
            'method': 'GET',
            'url': '/resourcetypes',
            'arguments': [ADDITIONAL_PARAMS_ARG],
            'decorators': DEFAULT_DECORATORS,
            'description': 'Query `resource type` entities.',
            'links': {
                'doc': 'query-resource-types',
                'apidoc': '',
            },
        },
    }
