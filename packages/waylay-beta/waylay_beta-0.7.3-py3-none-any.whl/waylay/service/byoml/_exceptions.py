"""Exceptions specific to the Byoml Service."""

from ...exceptions import (
    RestResponseError,
    RestResponseParseError,
    RequestError,
    RestError
)


class ByomlActionError(RestResponseError):
    """Error that represents the json messages of a byoml response."""

    @property
    def message(self):
        """Get the main user error returned by a byoml error response."""
        return self._get_from_body('error', super().message)


class ByomlActionParseError(RestResponseParseError, ByomlActionError):
    """Indicates that a byoml response could not be parsed."""


class ByomlValidationError(RequestError):
    """Exception class for BYOML validation errors."""


class ModelNotReadyError(RestError):
    """Indicates that a byoml action should be retried."""
