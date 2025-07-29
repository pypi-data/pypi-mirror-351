"""REST definitions for the import process entity of the etl service."""

from waylay.service import WaylayResource
from waylay.service import decorators

DEFAULT_DECORATORS = [decorators.exception_decorator, decorators.return_body_decorator]


class ImportResource(WaylayResource):
    """REST Resource for the import process entity of the etl service."""

    link_roots = {
        'doc': '${doc_url}/features/etl/?id='
    }

    actions = {
        'get': {
            'method': 'GET',
            'url': '/etl/import',
            'returns': [{
                'name': 'body',
                'type': 'dict',
                'description': 'A representation of the active or last ETL import process (if any).'
            }],
            'decorators': DEFAULT_DECORATORS,
            'description': "Retrieves the last or active etl import process.",
            'links': {
                'doc': 'etl-import-service',
            }
        }
    }
