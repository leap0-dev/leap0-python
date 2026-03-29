from __future__ import annotations

from dataclasses import dataclass
import os

from .constants import DEFAULT_BASE_URL, DEFAULT_SANDBOX_DOMAIN


DEFAULT_CLIENT_TIMEOUT = 300.0


@dataclass(slots=True)
class Leap0Config:
    """Configuration for a Leap0 client.

    Args:
        api_key: API key for authentication. Falls back to the LEAP0_API_KEY
            environment variable when ``None``.
        base_url: Base URL of the Leap0 control-plane API.
        sandbox_domain: Domain suffix used to build per-sandbox URLs.
        timeout: Default HTTP timeout in seconds.
        auth_header: Name of the header used to send the API key.
        bearer: When True, the key is sent with a ``Bearer`` prefix.
    """
    api_key: str | None = None
    base_url: str = DEFAULT_BASE_URL
    sandbox_domain: str | None = DEFAULT_SANDBOX_DOMAIN
    timeout: float = DEFAULT_CLIENT_TIMEOUT
    auth_header: str = "authorization"
    bearer: bool = True

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.environ.get("LEAP0_API_KEY")
        if not self.api_key:
            raise ValueError("api_key is required or set LEAP0_API_KEY")
