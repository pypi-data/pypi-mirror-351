"""Legacy placeholder for the Analytics REST service."""


class AnalyticsServiceLegacy:
    """Legacy placeholder."""

    @property
    def query(self):
        """Raise a unsupported issues."""
        raise NotImplementedError(
            'The `analytics.query` resource is no longer supported. Please use `queries.query`.'
        )

    @property
    def about(self):
        """Raise a unsupported issues."""
        raise NotImplementedError(
            'The `analytics` service is no longer supported. Please use `queries` service.'
        )
