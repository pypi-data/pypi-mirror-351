"""Utilities."""

from io import TextIOWrapper
from tempfile import SpooledTemporaryFile


class NonClosingTextIOWrapper(TextIOWrapper):
    """TextIOWrapper that doesn't close, but detaches the wrapped buffer when gc-ed."""

    # SEE https://bugs.python.org/issue21363
    # https://github.com/astropy/astropy/pull/11809/files#r644158123
    def __del__(self):
        """Detach from underlying buffer on deletion."""
        self.detach()


class WrappeableSpooledTemporaryFile(SpooledTemporaryFile):
    """Adapted SpooledTemporaryFile so it can be wrapped in a TextIOWrapper."""

    def readable(self) -> bool:
        """Assert readability."""
        return True

    def writable(self) -> bool:
        """Assert writability."""
        return True

    def seekable(self) -> bool:
        """Assert seekablity."""
        return True
