"""Decorators to be used in waylaycli."""
import logging

from functools import wraps
from waylay.exceptions import WaylayError

LOG = logging.getLogger(__name__)


def cli_exeption_decorator(action_method):
    """Create a decorator that handles exceptions for the cli tool."""
    @wraps(action_method)
    def wrapped(*args, **kwargs):
        try:
            return action_method(*args, **kwargs)
        except BrokenPipeError as exc:
            LOG.debug('Ignored broken pipe (stdout gone)', exc_info=True)
        except (WaylayError, ValueError, TypeError) as exc:
            LOG.error('\n'.join(exc.args), exc_info=LOG.isEnabledFor(logging.DEBUG))

    return wrapped
