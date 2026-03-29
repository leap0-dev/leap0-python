from __future__ import annotations


class Leap0Error(Exception):
    """Base exception for all Leap0 SDK errors."""


class Leap0APIError(Leap0Error):
    """Raised when the Leap0 API returns an unexpected HTTP status code.

    Attributes:
        status_code: HTTP status code returned by the API.
        message: Human-readable error description.
        body: Raw response body, if available.
    """

    def __init__(self, status_code: int, message: str, *, body: str | None = None):
        self.status_code = status_code
        self.message = message
        self.body = body
        detail = f"{status_code} {message}"
        if body:
            detail = f"{detail}: {body}"
        super().__init__(detail)


class Leap0WebSocketError(Leap0Error):
    """Raised when a WebSocket connection to a sandbox fails."""
