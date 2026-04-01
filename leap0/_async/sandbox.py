from __future__ import annotations

import inspect
import os
from functools import wraps
from typing import TYPE_CHECKING, Generic, Protocol, TypeVar, cast

from .._internal.types import SandboxFactory
from ..models.config import (
    DEFAULT_MEMORY_MIB,
    DEFAULT_TEMPLATE_NAME,
    DEFAULT_TIMEOUT_MIN,
    DEFAULT_VCPU,
    OTEL_EXPORTER_OTLP_ENDPOINT_ENV,
    OTEL_EXPORTER_OTLP_HEADERS_ENV,
)
from ..models.sandbox import CreateSandboxParams, Sandbox as SandboxData, SandboxRef, SandboxStatus, sandbox_id_of
from .._schemas.sandbox import NetworkPolicyDict, SandboxCreateResponseDict, SandboxStatusResponseDict
from .._utils.errors import intercept_errors
from .._utils.url import ensure_leading_slash, sandbox_base_url, websocket_url_from_http
from ._transport import AsyncTransport

AsyncSandboxT = TypeVar("AsyncSandboxT", SandboxData, SandboxStatus, "AsyncSandbox")

if TYPE_CHECKING:
    from .client import AsyncLeap0Client


_OTEL_ENV_KEYS = (
    OTEL_EXPORTER_OTLP_ENDPOINT_ENV,
    OTEL_EXPORTER_OTLP_HEADERS_ENV,
)


class _AsyncSandboxServiceProxy:
    def __init__(self, service: object, sandbox: AsyncSandbox):
        self._service = service
        self._sandbox = sandbox

    def __getattr__(self, name: str) -> object:
        attr = getattr(self._service, name)
        if not callable(attr):
            return attr
        if not inspect.iscoroutinefunction(attr):
            @wraps(attr)
            def sync_bound(*args: object, **kwargs: object) -> object:
                return attr(self._sandbox, *args, **kwargs)

            return sync_bound

        bound_attr = cast(_AsyncBoundSandboxCallable, attr)

        @wraps(attr)
        async def bound(*args: object, **kwargs: object) -> object:
            return await bound_attr(self._sandbox, *args, **kwargs)

        return bound


class _AsyncBoundSandboxCallable(Protocol):
    async def __call__(self, sandbox: object, *args: object, **kwargs: object) -> object: ...


class AsyncSandbox:
    """Sandbox object with bound asynchronous service clients.

    Attributes:
        filesystem: Bound filesystem client.
        git: Bound git client.
        process: Bound process client.
        pty: Bound PTY client.
        lsp: Bound LSP client.
        ssh: Bound SSH client.
        code_interpreter: Bound code interpreter client.
        desktop: Bound desktop client.
    """
    def __init__(self, client: "AsyncLeap0Client", data: SandboxData | SandboxStatus):
        self._client: "AsyncLeap0Client" = client
        self._data: SandboxData | SandboxStatus = data
        self.filesystem = _AsyncSandboxServiceProxy(client.filesystem, self)
        self.git = _AsyncSandboxServiceProxy(client.git, self)
        self.process = _AsyncSandboxServiceProxy(client.process, self)
        self.pty = _AsyncSandboxServiceProxy(client.pty, self)
        self.lsp = _AsyncSandboxServiceProxy(client.lsp, self)
        self.ssh = _AsyncSandboxServiceProxy(client.ssh, self)
        self.code_interpreter = _AsyncSandboxServiceProxy(client.code_interpreter, self)
        self.desktop = _AsyncSandboxServiceProxy(client.desktop, self)

    def __getattr__(self, name: str) -> object:
        return getattr(self._data, name)

    def __repr__(self) -> str:
        state = getattr(self._data, "state", None)
        return f"AsyncSandbox(id={self.id!r}, state={state!r})"

    async def refresh(self) -> AsyncSandbox:
        """Refresh this sandbox object with the latest metadata.

        Returns:
            AsyncSandbox: This sandbox object with refreshed metadata.
        """
        latest = await self._client.sandboxes.get(self.id)
        self._data = latest._data
        return self

    async def pause(self) -> AsyncSandbox:
        """Pause the sandbox and return updated metadata.

        Returns:
            AsyncSandbox: This sandbox object with updated metadata.
        """
        latest = await self._client.sandboxes.pause(self)
        self._data = latest._data
        return self

    async def delete(self, http_timeout: float | None = None) -> None:
        """Terminate and delete a sandbox.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        await self._client.sandboxes.delete(self, http_timeout=http_timeout)

    def invoke_url(self, path: str = "/", *, port: int | None = None) -> str:
        """Build an HTTPS URL for this sandbox.

        Args:
            path: Request path inside the sandbox application.
            port: Port number for the generated URL.

        Returns:
            str: Sandbox-scoped HTTPS URL.
        """
        return self._client.sandboxes.invoke_url(self, path=path, port=port)

    def websocket_url(self, path: str = "/", *, port: int | None = None) -> str:
        """Build a websocket URL for this sandbox.

        Args:
            path: Request path inside the sandbox application.
            port: Port number for the generated URL.

        Returns:
            str: Sandbox-scoped websocket URL.
        """
        return self._client.sandboxes.websocket_url(self, path=path, port=port)


def _inject_otel_env(env_vars: dict[str, str] | None) -> dict[str, str] | None:
    endpoint = os.environ.get(OTEL_EXPORTER_OTLP_ENDPOINT_ENV)
    if not endpoint:
        raise ValueError(
            f"otel_export=True requires {OTEL_EXPORTER_OTLP_ENDPOINT_ENV} in the local environment"
        )
    otel = {OTEL_EXPORTER_OTLP_ENDPOINT_ENV: endpoint}
    for key in _OTEL_ENV_KEYS:
        if key == OTEL_EXPORTER_OTLP_ENDPOINT_ENV:
            continue
        value = os.environ.get(key)
        if value:
            otel[key] = value
    merged = dict(otel)
    if env_vars:
        merged.update(env_vars)
    return merged


class AsyncSandboxesClient(Generic[AsyncSandboxT]):
    """Create, inspect, pause, and delete sandboxes asynchronously.

    Attributes:
        None.
    """
    def __init__(
        self,
        transport: AsyncTransport,
        *,
        sandbox_domain: str | None = None,
        sandbox_factory: SandboxFactory[SandboxData | SandboxStatus, AsyncSandboxT] | None = None,
    ):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None
        self._sandbox_factory = sandbox_factory

    def _wrap_sandbox(self, sandbox: SandboxData | SandboxStatus) -> AsyncSandboxT | SandboxData | SandboxStatus:
        if self._sandbox_factory is None:
            return sandbox
        return self._sandbox_factory(sandbox)

    @intercept_errors("Failed to create sandbox: ")
    async def create(
        self,
        *,
        template_name: str = DEFAULT_TEMPLATE_NAME,
        vcpu: int = DEFAULT_VCPU,
        memory_mib: int = DEFAULT_MEMORY_MIB,
        timeout_min: int = DEFAULT_TIMEOUT_MIN,
        auto_pause: bool = False,
        otel_export: bool = False,
        env_vars: dict[str, str] | None = None,
        network_policy: NetworkPolicyDict | None = None,
        http_timeout: float | None = None,
    ) -> AsyncSandboxT | SandboxData | SandboxStatus:
        """Create a new sandbox from a template.

        Args:
            template_name: Name of the template to use.
            vcpu: Number of virtual CPUs (1 to 8).
            memory_mib: Memory in MiB (512 to 8192, must be even).
            timeout_min: Sandbox timeout in minutes (1 to 480).
            auto_pause: Whether the sandbox should auto-pause on timeout.
            otel_export: Whether OpenTelemetry exporter variables should be injected.
            env_vars: Environment variables to set inside the sandbox.
            network_policy: Outbound network policy for the sandbox.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            AsyncSandboxT | SandboxData | SandboxStatus: Created sandbox object.
        """
        params = CreateSandboxParams(
            template_name=template_name,
            vcpu=vcpu,
            memory_mib=memory_mib,
            timeout_min=timeout_min,
            auto_pause=auto_pause,
            otel_export=otel_export,
            env_vars=_inject_otel_env(env_vars) if otel_export else env_vars,
            network_policy=network_policy,
        )
        payload = params.to_payload()
        payload.pop("otel_export", None)
        data: SandboxCreateResponseDict = await self._transport.request_json(
            "POST", "/v1/sandbox", json=payload, expected_status=201,
            timeout=http_timeout,
        )
        return self._wrap_sandbox(SandboxData.from_dict(data))

    @intercept_errors("Failed to pause sandbox: ")
    async def pause(self, sandbox: SandboxRef) -> AsyncSandboxT | SandboxData | SandboxStatus:
        """Pause the sandbox and return updated metadata.

        Args:
            sandbox: Sandbox ID or object.

        Returns:
            AsyncSandboxT | SandboxData | SandboxStatus: Updated sandbox object.
        """
        data: SandboxCreateResponseDict = await self._transport.request_json(
            "POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pause", expected_status=201
        )
        return self._wrap_sandbox(SandboxData.from_dict(data))

    @intercept_errors("Failed to get sandbox: ")
    async def get(self, sandbox: SandboxRef, http_timeout: float | None = None) -> AsyncSandboxT | SandboxData | SandboxStatus:
        """Get the latest sandbox metadata.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            AsyncSandboxT | SandboxData | SandboxStatus: Current sandbox object.
        """
        data: SandboxStatusResponseDict = await self._transport.request_json(
            "GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/",
            timeout=http_timeout,
        )
        return self._wrap_sandbox(SandboxStatus.from_dict(data))

    @intercept_errors("Failed to delete sandbox: ")
    async def delete(self, sandbox: SandboxRef, http_timeout: float | None = None) -> None:
        """Terminate and delete a sandbox.

        Args:
            sandbox: Sandbox ID or object.
        """
        await self._transport.request(
            "DELETE",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/",
            expected_status=204,
            timeout=http_timeout,
        )

    def invoke_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build an HTTPS URL for this sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            port: Port number for the generated URL.
        
        Returns:
            object: Result returned by this operation.
        """
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain, port=port)}{ensure_leading_slash(path)}"

    def websocket_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build a websocket URL for this sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            port: Port number for the generated URL.
        
        Returns:
            object: Result returned by this operation.
        """
        return websocket_url_from_http(self.invoke_url(sandbox, path, port=port))


__all__ = ["AsyncSandbox", "AsyncSandboxesClient"]
