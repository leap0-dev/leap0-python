from __future__ import annotations

import functools
import inspect
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Generator, Iterator
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import ParamSpec, NoReturn, TypeVar, cast

from ..models.errors import Leap0Error, Leap0TimeoutError

P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")


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
            retryable=getattr(exc, "retryable", False),
        ) from None

    try:
        import httpx as _httpx
    except ImportError:  # pragma: no cover
        _httpx = None  # type: ignore[assignment]

    if _httpx is not None:
        if isinstance(exc, _httpx.TimeoutException):
            raise Leap0TimeoutError(_prefixed_message(str(exc), prefix)) from None
        if isinstance(exc, (_httpx.ConnectError, _httpx.NetworkError)):
            raise Leap0Error(_prefixed_message(str(exc), prefix), retryable=True) from None

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


def _wrap_generator(
    gen: Iterator[T],
    message_prefix: str,
    transport: object | None = None,
    http_timeout: float | None = None,
) -> Generator[T, None, None]:
    """Yield from *gen* while applying the same error-normalisation logic."""
    try:
        if transport is not None:
            with _sync_timeout_override(transport, http_timeout):
                yield from gen
        else:
            yield from gen
    except Exception as exc:
        _raise_processed(message_prefix, exc)


async def _wrap_async_generator(
    gen: AsyncIterator[T],
    message_prefix: str,
    transport: object | None = None,
    http_timeout: float | None = None,
) -> AsyncGenerator[T, None]:
    try:
        if transport is not None:
            async with _async_timeout_override(transport, http_timeout):
                async for item in gen:
                    yield item
        else:
            async for item in gen:
                yield item
    except Exception as exc:
        _raise_processed(message_prefix, exc)


def _get_timeout_context(
    args: tuple[object, ...],
    kwargs: dict[str, object],
) -> tuple[object | None, float | None]:
    http_timeout = kwargs.get("http_timeout")
    if http_timeout is None or not args:
        return None, None
    transport = getattr(args[0], "_transport", None)
    if transport is None or not hasattr(transport, "override_timeout"):
        return None, None
    return transport, cast(float, http_timeout)


def _sync_timeout_override(
    transport: object,
    http_timeout: float | None,
) -> AbstractContextManager[object]:
    return cast(AbstractContextManager[object], getattr(transport, "override_timeout")(http_timeout))


def _async_timeout_override(
    transport: object,
    http_timeout: float | None,
) -> AbstractAsyncContextManager[object]:
    return cast(AbstractAsyncContextManager[object], getattr(transport, "override_timeout")(http_timeout))


# Error interception decorator
def intercept_errors(message_prefix: str = "") -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that normalizes transport and runtime failures into SDK errors.

    The decorator turns low-level exceptions into fresh ``Leap0Error`` subclasses with a
    clear method-specific prefix, while preserving HTTP metadata when it
    already exists on a caught ``Leap0Error``.

    When the decorated function is a generator (or returns an iterator), the
    error handling also covers exceptions raised during iteration.
    """

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        if inspect.isasyncgenfunction(fn):
            @functools.wraps(fn)
            def async_gen_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                try:
                    transport, http_timeout = _get_timeout_context(
                        cast(tuple[object, ...], args),
                        cast(dict[str, object], kwargs),
                    )
                    result = fn(*args, **kwargs)
                except Exception as exc:
                    _raise_processed(message_prefix, exc)
                else:
                    return cast(
                        R,
                        _wrap_async_generator(
                            cast(AsyncIterator[object], result),
                            message_prefix,
                            transport,
                            http_timeout,
                        ),
                    )

            return async_gen_wrapper

        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                try:
                    transport, http_timeout = _get_timeout_context(
                        cast(tuple[object, ...], args),
                        cast(dict[str, object], kwargs),
                    )
                    if transport is not None:
                        async with _async_timeout_override(transport, http_timeout):
                            return await fn(*args, **kwargs)
                    return await fn(*args, **kwargs)
                except Exception as exc:
                    _raise_processed(message_prefix, exc)

            return async_wrapper

        @functools.wraps(fn)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                transport, http_timeout = _get_timeout_context(
                    cast(tuple[object, ...], args),
                    cast(dict[str, object], kwargs),
                )
                if transport is not None:
                    with _sync_timeout_override(transport, http_timeout):
                        result = fn(*args, **kwargs)
                else:
                    result = fn(*args, **kwargs)
            except Exception as exc:
                _raise_processed(message_prefix, exc)
            else:
                if isinstance(result, (Iterator, Generator)) or inspect.isgenerator(result):
                    return cast(
                        R,
                        _wrap_generator(
                            cast(Iterator[object], result),
                            message_prefix,
                            transport,
                            http_timeout,
                        ),
                    )
                return result

        return wrapper

    return decorator
