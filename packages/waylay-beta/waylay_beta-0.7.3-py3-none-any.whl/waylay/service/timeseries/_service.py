"""Internal service with tools for timeseries import and export."""

from waylay.service import WaylayService, WaylayServiceContext
from waylay.config import WaylayConfig

from .tool import TimeSeriesETLTool


class TimeSeriesService(WaylayService):
    """Tool service for the timeseries import and export operations."""

    service_key = 'timeseries'

    etl_tool: TimeSeriesETLTool

    resource_definitions = {
        'etl_tool': TimeSeriesETLTool
    }

    def configure(self, config: WaylayConfig, context: WaylayServiceContext) -> 'TimeSeriesService':
        """Configure endpoints and authentication with given config."""
        super().configure(config, context)
        self.etl_tool.set_context(context)
        return self
