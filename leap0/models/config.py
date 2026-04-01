from __future__ import annotations

import math
import os
from pydantic import BaseModel, ConfigDict, model_validator

DEFAULT_BASE_URL = "https://api.leap0.dev"

DEFAULT_SANDBOX_DOMAIN = "sandbox.leap0.dev"

DEFAULT_TEMPLATE_NAME = "system/debian:bookworm"

DEFAULT_CODE_INTERPRETER_TEMPLATE_NAME = "system/code-interpreter:v0.1.0"

DEFAULT_DESKTOP_TEMPLATE_NAME = "system/desktop:v0.1.0"

DEFAULT_VCPU = 1

DEFAULT_MEMORY_MIB = 1024

DEFAULT_TIMEOUT_MIN = 5

DEFAULT_CLIENT_TIMEOUT = 300.0

OTEL_EXPORTER_OTLP_ENDPOINT_ENV = "OTEL_EXPORTER_OTLP_ENDPOINT"

OTEL_EXPORTER_OTLP_HEADERS_ENV = "OTEL_EXPORTER_OTLP_HEADERS"

def _resolve_env_str(value: str | None, env_var: str, default: str) -> str:
    resolved = value.strip() if value else None
    if not resolved:
        env_val = os.environ.get(env_var)
        resolved = env_val.strip() if env_val else None
    return resolved or default

class Leap0Config(BaseModel):
    """Configuration for a Leap0 client."""

    model_config = ConfigDict(extra="forbid")

    api_key: str | None = None
    base_url: str | None = None
    sandbox_domain: str | None = None
    timeout: float = DEFAULT_CLIENT_TIMEOUT
    auth_header: str = "authorization"
    bearer: bool = True
    sdk_otel_enabled: bool | None = None

    @model_validator(mode="after")
    def _resolve_and_validate(self) -> Leap0Config:
        try:
            timeout = float(self.timeout)
        except (TypeError, ValueError) as err:
            raise ValueError(f"timeout must be a positive number, got {self.timeout!r}") from err
        if timeout <= 0 or not math.isfinite(timeout):
            raise ValueError(f"timeout must be a positive, finite number, got {self.timeout!r}")

        api_key = self.api_key
        if api_key is None:
            api_key = os.environ.get("LEAP0_API_KEY")
        api_key = api_key.strip() if api_key else api_key
        if not api_key:
            raise ValueError("api_key is required or set LEAP0_API_KEY")

        auth_header = self.auth_header.strip()
        if not auth_header:
            raise ValueError("auth_header must be a non-empty string")

        self.timeout = timeout
        self.api_key = api_key
        self.auth_header = auth_header
        if self.sdk_otel_enabled is None:
            sdk_otel_env = os.environ.get("LEAP0_SDK_OTEL_ENABLED")
            sdk_otel_env = sdk_otel_env.strip() if sdk_otel_env is not None else None
            if sdk_otel_env:
                self.sdk_otel_enabled = sdk_otel_env.lower() == "true"
            else:
                self.sdk_otel_enabled = bool(os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT_ENV))
        self.base_url = _resolve_env_str(self.base_url, "LEAP0_BASE_URL", DEFAULT_BASE_URL)
        self.sandbox_domain = _resolve_env_str(
            self.sandbox_domain,
            "LEAP0_SANDBOX_DOMAIN",
            DEFAULT_SANDBOX_DOMAIN,
        )
        return self
