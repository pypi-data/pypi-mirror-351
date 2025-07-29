"""Exceptions specific to the Queries Service."""

from typing import (
    List, Mapping, Any
)
from ...exceptions import RestRequestError, RestResponseError, RestResponseParseError


class QueryActionError(RestResponseError):
    """Error that represents the json messages of a query response."""

    @property
    def messages(self) -> List[Mapping[str, Any]]:
        """Get the list of message objects returned by a query error response."""
        return self._get_from_body('messages', [])

    @property
    def message(self):
        """Get the main user error returned by a query error response."""
        return self._get_from_body('error', super().message)


class QueryActionParseError(RestResponseParseError, QueryActionError):
    """Indicates that a query response could not be parsed."""


class QueryRequestError(RestRequestError):
    """Indicates issues with the request arguments."""
