"""Resource action method decorators that are generally usefull."""

import time
from functools import wraps
from typing import (
    Union, List, Mapping, Any, Callable, TypeVar, Dict, Optional
)

from logging import Logger, getLevelName, INFO
from simple_rest_client.exceptions import ErrorWithResponse, ClientConnectionError
from ..exceptions import RestResponseError, RestResponseParseError, RestConnectionError


def suppress_header_decorator(header_key):
    """Create a decorator that suppresses a configured header on a resource during execution."""
    def decorator(action_method):
        @wraps(action_method)
        def wrapped(slf, *args, **kwargs):
            header_value = slf.headers.pop(header_key, None)
            try:
                return action_method(slf, *args, **kwargs)
            finally:
                if header_value:
                    slf.headers[header_key] = header_value
        return wrapped
    return decorator


def exception_decorator(action_method):
    """Create a decorator that parses json error responses."""
    @wraps(action_method)
    def wrapped(*args, **kwargs):
        try:
            return action_method(*args, **kwargs)
        except ErrorWithResponse as exc:
            raise RestResponseError.from_cause(exc) from exc
        except ClientConnectionError as exc:
            raise RestConnectionError.from_cause(exc) from exc
    return wrapped


def default_params_decorator(default_params: Dict[str, Any]):
    """Create a decorator that initializes default url request parameters."""
    def decorator(action_method):
        @wraps(action_method)
        def wrapped(*args, **kwargs):
            params = kwargs.pop('params', {})
            for key, value in default_params.items():
                if key not in params:
                    params[key] = value
            kwargs['params'] = params
            return action_method(*args, **kwargs)
        wrapped.__doc__ = (
            (wrapped.__doc__ or '') +
            "\nUses default url parameters (`params` argument):" +
            "".join(
                f"\n    '{key}': {default_value}"
                for key, default_value in default_params.items()
            ) + "\n"
        )
        return wrapped
    return decorator


def default_header_decorator(default_headers: Dict[str, Any]):
    """Create a decorator that initializes default header parameters."""
    def decorator(action_method):
        @wraps(action_method)
        def wrapped(*args, **kwargs):
            headers = kwargs.pop('headers', {})
            for key, value in default_headers.items():
                if key not in headers:
                    headers[key] = str(value)
            kwargs['headers'] = headers
            return action_method(*args, **kwargs)
        wrapped.__doc__ = (
            (wrapped.__doc__ or '') +
            "\nUses default headers (`headers` argument):" +
            "".join(
                f"\n    '{key}': {default_value}"
                for key, default_value in default_headers.items()
            ) + "\n"
        )
        return wrapped
    return decorator


def default_timeout_decorator(default_timeout: float):
    """Create a decorator that modifies the default http client timeout."""

    def decorator(action_method):
        @wraps(action_method)
        def wrapped(*args, **kwargs):
            timeout = kwargs.pop('timeout', default_timeout)
            return action_method(*args, timeout=timeout, **kwargs)
        timeout_arg = f'timeout={default_timeout}'
        wrapped.__doc__ = (
            (wrapped.__doc__ or '') + f"""
Uses a modified default http client timeout:"
    {timeout_arg:30}: Client timeout for the REST request.
""")
        return wrapped
    return decorator


T = TypeVar('T')


def identity_transform(obj: T) -> T:
    """Return the argument."""
    return obj


def return_path_decorator(
    default_path: List[Union[int, str]],
    default_response_constructor: Optional[Callable[[Any], Any]] = None,
    response_constructor_advice: str = ''
):
    """Create a decorator method that extracts a part of the json body of an action response.

    The 'default_path' is a list of 'int' or 'str' keys that select through
    'dict' and 'list' structures.
    The option 'response_constructor' wrap the value in a class or constructor method
    It processes the following qualified arguments in a method call:
    * if 'raw=True' is set, the original response is returned
    * if 'select_path' is set, that path is used rather than the 'default_path'
       provided in the decorator constructor.
    * if 'response_constructor' is set, it is used to wrap the response
      rather than 'default_response_constructor'
    """
    def decorator(action_method):
        @wraps(action_method)
        def wrapped(*args, **kwargs):
            raw = kwargs.pop('raw', False)
            select_path = kwargs.pop('select_path', default_path)
            constructor = kwargs.pop(
                'response_constructor', default_response_constructor
            ) or identity_transform
            response = action_method(*args, **kwargs)
            if raw:
                return response
            if response.status_code == 204:
                # No-Content
                return None
            try:
                return constructor(
                    _select_path_from(response.body, [], select_path)
                )
            except AttributeError as exc:
                raise RestResponseParseError(exc.args[0], response) from exc
        resp_constr_arg = 'response_constructor'
        if default_response_constructor:
            resp_constr_arg += f"={_fqn_name(default_response_constructor)}"
        select_path_arg = f"select_path={default_path}"
        raw_arg = 'raw=False'
        dec_doc = (
            f"""
Returns the (parsed json) response body. Arguments that configure response handling:
    {select_path_arg:30}: extract path from the response body.
    {resp_constr_arg:30}: transforms the extracted response. {response_constructor_advice}
    {raw_arg:30}: If `True`, returns unmodified http response information.
"""
        )
        wrapped.__doc__ = (wrapped.__doc__ or '') + dec_doc
        return wrapped
    return decorator


def _fqn_name(func: Any) -> str:
    if func.__module__ == 'builtins':
        return func.__qualname__
    return f"{func.__module__}.{func.__qualname__}"


def return_body_decorator(action_method):
    """Create a decorator that returns the body of an action response.

    Skipped if 'raw=True' is provided in the call.
    """
    return return_path_decorator([])(action_method)


def _select_path_from(
    value: Any, ctx_path: List[Union[int, str]], path: List[Union[int, str]]
) -> Any:
    # Recursively select values from 'Mapping' (dict, 'str' key) input,
    # or positional elements from 'List' (list, 'int' key) input,
    # with a 'path' consisting of a list of keys.
    # Applied keys are moved to the 'ctx_path' to be used for error reporting.
    # 'str' keys applied to a 'List' are mapped through to the underlying structure.

    if not path:
        return value
    key = path[0]
    new_ctx_path = ctx_path + [key]
    rem_path = path[1:]
    if isinstance(value, List):
        if isinstance(key, int) and len(value) < key:
            return _select_path_from(value[key], new_ctx_path, rem_path)
        if isinstance(key, str):
            return [
                _select_path_from(element[key], new_ctx_path, rem_path)
                for element in value
            ]
    if isinstance(value, Mapping) and isinstance(key, str) and key in value:
        return _select_path_from(value[key], new_ctx_path, rem_path)

    ctx_path_str = '.'.join(str(p) for p in new_ctx_path)
    raise AttributeError(f"Cannot find '{ctx_path_str}' in response body.")


def log_server_timing_decorator(logger: Optional[Logger] = None, level: int = INFO):
    """Create a decorator that inspects and logs a 'Server-Timing' response header.

    This decorator should be below any response or exception decorator.
    """
    def decorator(action_method):
        logger.debug(
            'enabled Server-Timing logging for %s at %s',
            action_method.action, getLevelName(level)
        )

        def _log_server_timing(server_timing, start):
            if server_timing is None:
                end = time.time()
                logger.log(level, 'no-server-timing-available;dur=%.3f', (end-start) / 1000)
                return
            for line in server_timing.split(','):
                logger.log(level, line.strip())

        @wraps(action_method)
        def wrapped(*args, **kwargs):
            start = time.time()
            try:
                response = action_method(*args, **kwargs)
                _log_server_timing(response.headers.get('Server-Timing', None), start)
                return response
            except ErrorWithResponse as exc:
                _log_server_timing(exc.response.headers.get('Server-Timing', None), start)
                raise exc
            except Exception:
                _log_server_timing(None, start)
                raise
        wrapped.__doc__ = (
            (wrapped.__doc__ or '') +
            f"\nLogs server timing on {logger.name} at level {getLevelName(level)}\n"
        )
        return wrapped
    return decorator


def add_decorator_docs(decorators):
    """Add the documentation of the given decorators to a method.

    Intended for methods that delegate to action methods with the given decorators.
    """
    def update_doc(method):
        method.__doc__ = (method.__doc__ or '') + "\n\n".join(
            _extract_doc(dec) for dec in decorators
        )
        return method

    return update_doc


def _extract_doc(decorator):
    def _dummy(): pass
    return decorator(_dummy).__doc__ or ''
