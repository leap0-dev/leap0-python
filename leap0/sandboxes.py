from __future__ import annotations

import os
from typing import Any

from ._transport import Transport
from ._utils.errors import intercept_errors
from ._utils.url import ensure_leading_slash, sandbox_base_url, websocket_url_from_http
from .common.config import DEFAULT_MEMORY_MIB, DEFAULT_TEMPLATE_NAME, DEFAULT_TIMEOUT_MIN, DEFAULT_VCPU
from .common.sandbox import (
    NetworkPolicyDict, Sandbox, SandboxCreateResponseDict, SandboxRef,
    SandboxStatus, SandboxStatusResponseDict, sandbox_id_of,
)


_OTEL_ENV_KEYS = (
    "OTEL_EXPORTER_OTLP_ENDPOINT",
    "OTEL_EXPORTER_OTLP_HEADERS",
)


def _inject_otel_env(env_vars: dict[str, str] | None) -> dict[str, str] | None:
    otel = {k: v for k in _OTEL_ENV_KEYS if (v := os.environ.get(k))}
    if not otel and not env_vars:
        return None
    if not otel:
        return env_vars
    merged = dict(otel)
    if env_vars:
        merged.update(env_vars)
    return merged


class SandboxesClient:
    """Create, inspect, pause, and delete sandboxes."""

    def __init__(self, transport: Transport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    @intercept_errors("Failed to create sandbox: ")
    def create(
        self,
        *,
        template_name: str = DEFAULT_TEMPLATE_NAME,
        vcpu: int = DEFAULT_VCPU,
        memory_mib: int = DEFAULT_MEMORY_MIB,
        timeout_min: int = DEFAULT_TIMEOUT_MIN,
        auto_pause: bool = False,
        telemetry: bool = False,
        env_vars: dict[str, str] | None = None,
        network_policy: NetworkPolicyDict | None = None,
    ) -> Sandbox:
        """Create a new sandbox from a template.

        Args:
            template_name: Name of the template to use.
            vcpu: Number of virtual CPUs (1 to 8).
            memory_mib: Memory in MiB (512 to 8192, must be even).
            timeout_min: Sandbox timeout in minutes (1 to 480, default 5).
            auto_pause: Automatically pause the sandbox into a snapshot on timeout.
            telemetry: Enable OpenTelemetry export. Reads ``OTEL_EXPORTER_OTLP_ENDPOINT``
                and ``OTEL_EXPORTER_OTLP_HEADERS`` from the local environment and
                injects them into the sandbox.
            env_vars: Environment variables to set inside the sandbox.
            network_policy: Outbound network policy for the sandbox.
        """
        merged_env = _inject_otel_env(env_vars) if telemetry else env_vars

        payload: dict[str, Any] = {
            "template_name": template_name,
            "vcpu": vcpu,
            "memory_mib": memory_mib,
            "timeout_min": timeout_min,
            "auto_pause": auto_pause,
        }
        if merged_env is not None:
            payload["env_vars"] = merged_env
        if network_policy is not None:
            payload["network_policy"] = network_policy
        data: SandboxCreateResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST", "/v1/sandbox", json=payload, expected_status=201,
        )
        return Sandbox.from_dict(data)

    @intercept_errors("Failed to pause sandbox: ")
    def pause(self, sandbox: SandboxRef) -> Sandbox:
        """Pause a running sandbox. The sandbox must be in the ``running`` state."""
        data: SandboxCreateResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pause", expected_status=201,
        )
        return Sandbox.from_dict(data)

    @intercept_errors("Failed to get sandbox: ")
    def get(self, sandbox: SandboxRef) -> SandboxStatus:
        """Get the current status of a sandbox."""
        data: SandboxStatusResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/",
        )
        return SandboxStatus.from_dict(data)

    @intercept_errors("Failed to delete sandbox: ")
    def delete(self, sandbox: SandboxRef) -> None:
        """Terminate and delete a sandbox."""
        self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/", expected_status=204)

    def invoke_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build an HTTPS URL that routes directly to the sandbox.

        Args:
            sandbox: Sandbox ID or object.
            path: Path to append after the host.
            port: Optional port prefix for the sandbox subdomain.
        """
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain, port=port)}{ensure_leading_slash(path)}"

    def websocket_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build a WSS URL that routes directly to the sandbox."""
        return websocket_url_from_http(self.invoke_url(sandbox, path, port=port))
