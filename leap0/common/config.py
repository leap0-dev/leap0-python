from __future__ import annotations

import math
import os
from dataclasses import dataclass


DEFAULT_BASE_URL = "https://api.leap0.dev"
DEFAULT_SANDBOX_DOMAIN = "sandbox.leap0.dev"
DEFAULT_TEMPLATE_NAME = "system/code-interpreter:v0.1.0"
DEFAULT_DESKTOP_TEMPLATE_NAME = "system/desktop:v0.1.0"
DEFAULT_VCPU = 1
DEFAULT_MEMORY_MIB = 1024
DEFAULT_TIMEOUT_MIN = 5
DEFAULT_CLIENT_TIMEOUT = 300.0


def _resolve_env_str(
    value: str | None, env_var: str, default: str,
) -> str:
    """Return *value* (stripped) if non-empty, else the environment variable
    *env_var* (stripped), else *default*.

    Handles ``None`` and whitespace-only strings for both the provided
    value and the environment variable.
    """
    resolved = value.strip() if value else None
    if not resolved:
        env_val = os.environ.get(env_var)
        resolved = env_val.strip() if env_val else None
    return resolved or default


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
        timeout: Default HTTP timeout in seconds.  Must be a positive, finite
            number.
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
        # Validate and normalise timeout early, before it is used downstream.
        if self.timeout is None:
            raise ValueError("timeout must be a positive number, got None")
        try:
            self.timeout = float(self.timeout)
        except (TypeError, ValueError) as err:
            raise ValueError(
                f"timeout must be a positive number, got {self.timeout!r}"
            ) from err
        if self.timeout <= 0 or not math.isfinite(self.timeout):
            raise ValueError(
                f"timeout must be a positive, finite number, got {self.timeout!r}"
            )

        # Resolve api_key from env if not provided, then strip and validate.
        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("LEAP0_API_KEY")
        self.api_key = api_key.strip() if api_key else api_key
        if not self.api_key:
            raise ValueError("api_key is required or set LEAP0_API_KEY")

        self.base_url = _resolve_env_str(
            self.base_url, "LEAP0_BASE_URL", DEFAULT_BASE_URL,
        )
        self.sandbox_domain = _resolve_env_str(
            self.sandbox_domain, "LEAP0_SANDBOX_DOMAIN", DEFAULT_SANDBOX_DOMAIN,
        )
