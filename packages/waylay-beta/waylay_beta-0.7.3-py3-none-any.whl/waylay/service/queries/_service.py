
"""REST client for the Waylay Queries Service."""

from .._base import WaylayRESTService

from .query import QueryResource
from .about import AboutResource


class QueriesService(WaylayRESTService):
    """REST client for the Waylay Queries Service."""

    service_key = 'queries'
    config_key = 'query'
    gateway_root_path = '/queries/v1'
    default_root_path = '/queries/v1'

    resource_definitions = {
        'query': QueryResource,
        'about': AboutResource
    }
    query: QueryResource
    about: AboutResource

    def __init__(self):
        """Create a QueriesService."""
        super().__init__(json_encode_body=True)
