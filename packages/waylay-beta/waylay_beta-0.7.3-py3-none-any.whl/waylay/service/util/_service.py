
"""Utility tools and services for the Python SDK."""

from waylay.service import WaylayService, WaylayServiceContext
from waylay.config import WaylayConfig

from .info import InfoTool


class UtilService(WaylayService):
    """Utility Service for the python SDK."""

    service_key = 'util'

    info: InfoTool

    resource_definitions = {
        'info': InfoTool
    }

    def configure(self, config: WaylayConfig, context: WaylayServiceContext) -> 'UtilService':
        """Configure endpoints and authentication with given config."""
        super().configure(config, context)
        self.info.set_context(context)
        return self
