from __future__ import annotations

from dataclasses import dataclass
import os

from .constants import DEFAULT_BASE_URL, DEFAULT_SANDBOX_DOMAIN


DEFAULT_CLIENT_TIMEOUT = 300.0


@dataclass(slots=True)
class Leap0Config:
    """Configuration for a Leap0 client.

    Args:
        api_key: API key for authentication. Falls back to the ``LEAP0_API_KEY``
            environment variable when ``None``.
        base_url: Base URL of the Leap0 control-plane API. Falls back to the
            ``LEAP0_BASE_URL`` environment variable, then to
            ``https://api.leap0.dev``.
        sandbox_domain: Domain suffix used to build per-sandbox URLs.  Falls
            back to the ``LEAP0_SANDBOX_DOMAIN`` environment variable, then to
            ``sandbox.leap0.dev``.
        timeout: Default HTTP timeout in seconds.
        auth_header: Name of the header used to send the API key.
        bearer: When True, the key is sent with a ``Bearer`` prefix.
    """
    api_key: str | None = None
    base_url: str | None = None
    sandbox_domain: str | None = None
    timeout: float = DEFAULT_CLIENT_TIMEOUT
    auth_header: str = "authorization"
    bearer: bool = True

    def __post_init__(self) -> None:
        if self.api_key is None:
            self.api_key = os.environ.get("LEAP0_API_KEY")
        if not self.api_key:
            raise ValueError("api_key is required or set LEAP0_API_KEY")
        if self.base_url is None:
            self.base_url = os.environ.get("LEAP0_BASE_URL") or DEFAULT_BASE_URL
        if self.sandbox_domain is None:
            self.sandbox_domain = os.environ.get("LEAP0_SANDBOX_DOMAIN") or DEFAULT_SANDBOX_DOMAIN
