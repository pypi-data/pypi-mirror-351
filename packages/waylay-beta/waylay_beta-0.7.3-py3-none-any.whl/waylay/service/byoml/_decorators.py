"""Resource action method decorators specific for the 'byoml' service."""

from functools import wraps
import logging
from tenacity import (
    Retrying,
    RetryCallState,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
    retry_if_exception
)

from simple_rest_client.exceptions import (
    ErrorWithResponse, ClientConnectionError
)

from waylay.exceptions import RestConnectionError
from waylay.service._base import WaylayAction
from ._exceptions import ByomlActionError, ByomlActionParseError, ModelNotReadyError

DEFAULT_BYOML_MODEL_TIMEOUT = 60
TEMPORARY_FAILURES = [
    409,
    429,
    500,
    502,
    503,
    504,
    508
]
TEMPORARY_FAILURE_EXCEPTIONS = [
    ModelNotReadyError
]
WAIT_EXPONENTIAL = {
    "multiplier": 1,
    "min": 4,
    "max": 32
}
DEFAULT_RETRY_ATTEMPTS = 20
DEFAULT_RETRY_MAX_DELAY = 180


def before_sleep_logger(action: WaylayAction, logger=None, level=logging.WARNING):
    """Create a before-sleep log function for tenacity.Retrying."""
    logger = logger or logging.getLogger(action.fqn)

    def _log_before_sleep(retry_state: RetryCallState) -> None:
        next_action = retry_state.next_action
        outcome = retry_state.outcome
        assert next_action and outcome
        logger.log(
            level,
            "Retrying %s in %s seconds as it raised %s.",
            action.fqn,
            next_action.sleep,
            outcome.exception()
        )
    return _log_before_sleep


def byoml_exception_decorator(action_method):
    """Create a decorator that parses json error responses."""
    @wraps(action_method)
    def wrapped(*args, **kwargs):
        try:
            return action_method(*args, **kwargs)
        except ErrorWithResponse as exc:
            raise ByomlActionError.from_cause(exc) from exc
        except ClientConnectionError as exc:
            raise RestConnectionError.from_cause(exc) from exc
    return wrapped


def byoml_raise_not_ready_get(action_method):
    """Create a decorator that retries after certain exceptions."""
    @wraps(action_method)
    def wrapped(*args, **kwargs):
        retry_until_ready = kwargs.pop('retry_until_ready', False)
        response = action_method(*args, **kwargs)
        if retry_until_ready:
            is_ready = response.body.get('ready', None)
            if is_ready is None:
                raise ByomlActionParseError('Failed to extract `ready` attribute', response)
            if not is_ready:
                raise ModelNotReadyError('Model is not ready yet.')
        return response
    retry_until_ready_arg = f'retry_until_ready=False'
    wrapped.__doc__ = ((wrapped.__doc__ or '') + f"""
The response contains a 'ready' attribute that indicates whether the model is ready to serve.
    {retry_until_ready_arg:30}: If true, raise an error handled by the retry mechanism when not ready.
""")
    return wrapped


def byoml_retry_upload_after_deletion_decorator(action_method):
    """
    Create a decorator that retries uploading a model.

    Occurs after a model with the same name has been deleted.
    """

    @wraps(action_method)
    def wrapped(*args, **kwargs):
        before_sleep = before_sleep_logger(action_method.action)
        retry_max_delay = kwargs.pop('retry_max_delay', DEFAULT_RETRY_MAX_DELAY)
        # if timeout is not explicitely given, align with retry_max_delay
        timeout = kwargs.pop('timeout', retry_max_delay)
        for attempt in Retrying(
            stop=(stop_after_delay(retry_max_delay)),
            retry=retry_if_exception(is_409_error),
            before_sleep=before_sleep,
            wait=wait_exponential(**WAIT_EXPONENTIAL),
            reraise=True
        ):
            with attempt:
                # reset input stream when retrying upload
                body = kwargs.get('body', None)
                if body and hasattr(body, 'seek'):
                    body.seek(0)
                return action_method(*args, timeout=timeout, **kwargs)

    retry_max_delay_arg = f'retry_max_delay={DEFAULT_RETRY_MAX_DELAY}'
    wrapped.__doc__ = ((wrapped.__doc__ or '') + f"""
Retries on upload after a deletion of a model with the same name has occurred (HTTP status code: 409).
Arguments that configure retry:
    {retry_max_delay_arg:30}: Maximal delay in seconds.
""")
    return wrapped


def byoml_retry_decorator(action_method):
    """Create a decorator that retries after certain exceptions."""

    @wraps(action_method)
    def wrapped(*args, **kwargs):
        before_sleep = before_sleep_logger(action_method.action)
        retry_attempts = kwargs.pop('retry_attempts', DEFAULT_RETRY_ATTEMPTS)
        retry_max_delay = kwargs.pop('retry_max_delay', DEFAULT_RETRY_MAX_DELAY)
        # if timeout is not explicitely given, align with retry_max_delay
        timeout = kwargs.pop('timeout', retry_max_delay)
        for attempt in Retrying(
            stop=(stop_after_attempt(retry_attempts) | stop_after_delay(retry_max_delay)),
            retry=retry_if_exception(is_retry_failure),
            before_sleep=before_sleep,
            wait=wait_exponential(**WAIT_EXPONENTIAL),
            reraise=True
        ):
            with attempt:
                return action_method(*args, timeout=timeout, **kwargs)

    retry_attempts_arg = f'retry_attempts={DEFAULT_RETRY_ATTEMPTS}'
    retry_max_delay_arg = f'retry_max_delay={DEFAULT_RETRY_MAX_DELAY}'
    wrapped.__doc__ = ((wrapped.__doc__ or '') + f"""
Retries on temporary failures (HTTP status codes {', '.join(str(c) for c in TEMPORARY_FAILURES)}).
Arguments that configure retry:
    {retry_attempts_arg:30}: Maximal number of retries.
    {retry_max_delay_arg:30}: Maximal delay in seconds.
""")
    return wrapped


def is_retry_failure(exc):
    """Check if exception is a custom error or temporary error."""
    return is_temporary_failure_exception(exc) or is_temporary_failure(exc)


def is_temporary_failure_exception(exc):
    """Check if a given exception is a custom temporary failure exception."""
    return type(exc) in TEMPORARY_FAILURE_EXCEPTIONS


def is_temporary_failure(exc):
    """Check if given exception is temporary."""
    return hasattr(exc, "response") and exc.response.status_code in TEMPORARY_FAILURES


def is_409_error(exc):
    """Check if given exception is a 409 error."""
    return hasattr(exc, 'response') and exc.response.status_code == 409
