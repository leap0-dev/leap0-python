from __future__ import annotations

import functools
import inspect
from typing import Any, AsyncGenerator, Callable, Generator, Iterator, NoReturn, TypeVar, cast

from ..models.errors import Leap0Error, Leap0TimeoutError

F = TypeVar("F", bound=Callable[..., Any])


_HTTPX_CLOSED_CLIENT_MESSAGES = (
    "client has been closed",
    "cannot send a request, as the client has been closed",
)


def _prefixed_message(message: str, message_prefix: str) -> str:
    if not message_prefix or message.startswith(message_prefix):
        return message
    return f"{message_prefix}{message}"


def _raise_processed(prefix: str, exc: Exception) -> NoReturn:
    """Raise a fresh SDK exception with consistent normalization."""
    if isinstance(exc, Leap0Error):
        raise exc.__class__(
            _prefixed_message(exc.message, prefix),
            status_code=exc.status_code,
            headers=exc.headers,
            body=exc.body,
        ) from None

    try:
        import httpx as _httpx
    except ImportError:  # pragma: no cover
        _httpx = None  # type: ignore[assignment]

    if _httpx is not None:
        if isinstance(exc, _httpx.TimeoutException):
            raise Leap0TimeoutError(_prefixed_message(str(exc), prefix)) from None
        if isinstance(exc, (_httpx.ConnectError, _httpx.NetworkError)):
            raise Leap0Error(_prefixed_message(str(exc), prefix)) from None

    if isinstance(exc, RuntimeError):
        lowered = str(exc).lower()
        if any(message in lowered for message in _HTTPX_CLOSED_CLIENT_MESSAGES):
            raise Leap0Error(
                _prefixed_message(
                    (
                        f"{exc}: Leap0 client is closed. "
                        "Create a new client or keep operations within the client's context manager."
                    ),
                    prefix,
                )
            ) from None

    raise Leap0Error(_prefixed_message(str(exc), prefix)) from exc


def _wrap_generator(gen: Iterator[Any], message_prefix: str) -> Generator[Any, Any, Any]:
    """Yield from *gen* while applying the same error-normalisation logic."""
    try:
        yield from gen
    except Exception as exc:
        _raise_processed(message_prefix, exc)


async def _wrap_async_generator(gen: Any, message_prefix: str) -> AsyncGenerator[Any, Any]:
    try:
        async for item in gen:
            yield item
    except Exception as exc:
        _raise_processed(message_prefix, exc)


def _get_timeout_context(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any | None, float | None]:
    http_timeout = kwargs.get("http_timeout")
    if http_timeout is None or not args:
        return None, None
    transport = getattr(args[0], "_transport", None)
    if transport is None or not hasattr(transport, "override_timeout"):
        return None, None
    return transport, cast(float, http_timeout)


# Error interception decorator
def intercept_errors(message_prefix: str = "") -> Callable[[F], F]:
    """Decorator that normalizes transport and runtime failures into SDK errors.

    The decorator turns low-level exceptions into fresh ``Leap0Error`` subclasses with a
    clear method-specific prefix, while preserving HTTP metadata when it
    already exists on a caught ``Leap0Error``.

    When the decorated function is a generator (or returns an iterator), the
    error handling also covers exceptions raised during iteration.
    """

    def decorator(fn: F) -> F:
        if inspect.isasyncgenfunction(fn):
            @functools.wraps(fn)
            async def async_gen_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    transport, http_timeout = _get_timeout_context(args, kwargs)
                    if transport is not None:
                        async with transport.override_timeout(http_timeout):
                            result = fn(*args, **kwargs)
                    else:
                        result = fn(*args, **kwargs)
                except Exception as exc:
                    _raise_processed(message_prefix, cast(Exception, exc))
                else:
                    return _wrap_async_generator(result, message_prefix)

            return async_gen_wrapper  # type: ignore[return-value]

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    transport, http_timeout = _get_timeout_context(args, kwargs)
                    if transport is not None:
                        async with transport.override_timeout(http_timeout):
                            return await fn(*args, **kwargs)
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    _raise_processed(message_prefix, cast(Exception, exc))

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                transport, http_timeout = _get_timeout_context(args, kwargs)
                if transport is not None:
                    with transport.override_timeout(http_timeout):
                        result = fn(*args, **kwargs)
                else:
                    result = fn(*args, **kwargs)
            except Exception as exc:
                _raise_processed(message_prefix, cast(Exception, exc))
            else:
                if isinstance(result, (Iterator, Generator)) or inspect.isgenerator(result):
                    return _wrap_generator(result, message_prefix)
                return result

        return wrapper  # type: ignore[return-value]

    return decorator
