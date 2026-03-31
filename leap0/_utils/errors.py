from __future__ import annotations

import functools
from typing import Any, Callable, TypeVar

from ..common.errors import Leap0Error, Leap0TimeoutError

F = TypeVar("F", bound=Callable[..., Any])


# Error interception decorator
def intercept_errors(message_prefix: str = "") -> Callable[[F], F]:
    """Decorator that catches all exceptions and normalises them into
    ``Leap0Error`` subclasses with a human-readable *message_prefix*.

    This wraps:
    - ``Leap0Error`` -- re-raised with the prefix prepended.
    - ``httpx.TimeoutException`` -- converted to ``Leap0TimeoutError``.
    - ``httpx.ConnectError`` / ``httpx.NetworkError`` -- converted to ``Leap0Error``.
    - Any other ``Exception`` -- wrapped in ``Leap0Error``.
    """

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except Leap0Error as exc:
                if message_prefix and not exc.message.startswith(message_prefix):
                    exc.message = f"{message_prefix}{exc.message}"
                    detail = exc.message
                    if exc.status_code is not None:
                        detail = f"{exc.status_code} {detail}"
                    if exc.error_message:
                        detail = f"{detail}: {exc.error_message}"
                    elif exc.body:
                        detail = f"{detail}: {exc.body}"
                    exc.args = (detail,)
                raise
            except Exception as exc:
                _raise_wrapped(message_prefix, exc)

        return wrapper  # type: ignore[return-value]

    return decorator


def _raise_wrapped(prefix: str, exc: Exception) -> None:
    """Convert a non-SDK exception into the appropriate ``Leap0Error``."""
    try:
        import httpx as _httpx
    except ImportError:  # pragma: no cover
        _httpx = None  # type: ignore[assignment]

    if _httpx is not None:
        if isinstance(exc, _httpx.TimeoutException):
            raise Leap0TimeoutError(f"{prefix}{exc}") from exc
        if isinstance(exc, (_httpx.ConnectError, _httpx.NetworkError)):
            raise Leap0Error(f"{prefix}{exc}") from exc

    raise Leap0Error(f"{prefix}{exc}") from exc
