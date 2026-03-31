from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


class Leap0Error(Exception):
    """Base error for the Leap0 SDK.

    Every SDK exception carries optional HTTP context so callers can
    inspect the original response without parsing strings.

    Attributes:
        message: Human-readable error description.
        status_code: HTTP status code, if the error originated from an API response.
        headers: Response headers from the API, if available.
        error_message: Parsed ``message`` field from a JSON response body, if present.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        headers: Mapping[str, Any] | None = None,
        *,
        body: str | None = None,
    ):
        self.message = message
        self.status_code: int | None = status_code
        self.headers: dict[str, Any] = dict(headers or {})
        self.body: str | None = body
        self.error_message: str | None = None
        if body:
            try:
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    self.error_message = parsed.get("message")
            except (json.JSONDecodeError, TypeError):
                pass
        detail = message
        if status_code is not None:
            detail = f"{status_code} {detail}"
        if self.error_message:
            detail = f"{detail}: {self.error_message}"
        elif body:
            detail = f"{detail}: {body}"
        super().__init__(detail)


class Leap0NotFoundError(Leap0Error):
    """The requested resource does not exist (HTTP 404).

    Raised when a sandbox, file, directory, PTY session, LSP server,
    SSH access, or other resource cannot be found.
    """


class Leap0PermissionError(Leap0Error):
    """Permission denied for the requested operation (HTTP 403).

    Raised when the sandbox filesystem denies access due to
    file permissions or ownership.
    """


class Leap0ConflictError(Leap0Error):
    """The operation conflicts with the current resource state (HTTP 409).

    Raised when a resource already exists (e.g. ``mkdir`` on an existing
    directory), or when there are too many active sessions.
    """


class Leap0RateLimitError(Leap0Error):
    """Rate limit exceeded (HTTP 429).

    Callers should back off and retry after the interval indicated
    by the ``Retry-After`` header, if present.
    """


class Leap0TimeoutError(Leap0Error):
    """The operation timed out.

    Raised when a sandbox operation or API call exceeds its deadline.
    """


class Leap0WebSocketError(Leap0Error):
    """A WebSocket connection to a sandbox failed."""


# Status-code mapping used by the transport layer
_STATUS_TO_EXCEPTION: dict[int, type[Leap0Error]] = {
    403: Leap0PermissionError,
    404: Leap0NotFoundError,
    409: Leap0ConflictError,
    429: Leap0RateLimitError,
}


def raise_api_error(
    status_code: int,
    message: str,
    *,
    body: str | None = None,
    headers: Mapping[str, Any] | None = None,
) -> None:
    """Raise the most specific ``Leap0Error`` subclass for *status_code*.

    Unmapped codes (400, 401, 422, 500, 502, 503, etc.) produce a plain
    ``Leap0Error`` with the ``status_code`` attribute set so callers can
    still branch on it when needed.
    """
    cls = _STATUS_TO_EXCEPTION.get(status_code, Leap0Error)
    raise cls(message, status_code, headers, body=body)
