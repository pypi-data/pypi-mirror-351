"""REST client for the Waylay ETL Service."""

from waylay.service import WaylayRESTService

from .import_ import ImportResource


class ETLService(WaylayRESTService):
    """REST client for the Waylay ETL Service."""

    config_key = 'etl'
    service_key = 'etl'
    gateway_root_path = '/etl/v1'
    resource_definitions = {
        'etl_import': ImportResource,
    }

    etl_import: ImportResource
