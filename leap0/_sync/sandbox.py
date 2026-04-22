from __future__ import annotations

import os
from functools import wraps
from typing import Generic, Protocol, TypeVar, cast

from ..constants import OTEL_EXPORTER_OTLP_ENDPOINT_ENV, OTEL_EXPORTER_OTLP_HEADERS_ENV
from .._internal.types import SandboxFactory, SandboxHandle
from ..models.config import (
    DEFAULT_MEMORY_MIB,
    DEFAULT_TEMPLATE_NAME,
    DEFAULT_TIMEOUT,
    DEFAULT_VCPU,
)
from ..models.sandbox import (
    CreateSnapshotParams,
    CreatePresignedURLParams,
    CreateSandboxParams,
    ObjectStorageMount,
    PresignedURL,
    Sandbox as SandboxData,
    SandboxListResponse,
    SandboxRef,
    SandboxStatus,
    _validate_object_storage_mount_update,
    sandbox_id_of,
)
from ..models.snapshot import Snapshot
from .._schemas.snapshot import SnapshotCreateResponseDict
from .._schemas.sandbox import ListSandboxesResponseDict, NetworkPolicyDict, ObjectStorageMountDict, ObjectStorageMountRequestDict, ObjectStorageMountUpdateDict, PresignedURLResponseDict, SandboxCreateResponseDict, SandboxStatusResponseDict
from .._utils.errors import intercept_errors
from .._utils.url import ensure_leading_slash, sandbox_base_url, websocket_url_from_http
from ._transport import Transport


_OTEL_ENV_KEYS = (
    OTEL_EXPORTER_OTLP_ENDPOINT_ENV,
    OTEL_EXPORTER_OTLP_HEADERS_ENV,
)

SandboxT = TypeVar("SandboxT", SandboxData, SandboxStatus, "Sandbox")


class _BoundSandboxCallable(Protocol):
    def __call__(self, sandbox: object, *args: object, **kwargs: object) -> object: ...


class _SandboxServiceProxy:
    """Bind a service client to a specific sandbox instance."""

    def __init__(self, service: object, sandbox: Sandbox):
        self._service = service
        self._sandbox = sandbox

    def __getattr__(self, name: str) -> object:
        attr = getattr(self._service, name)
        if not callable(attr):
            return attr

        bound_attr = cast(_BoundSandboxCallable, attr)

        @wraps(attr)
        def bound(*args: object, **kwargs: object) -> object:
            return bound_attr(self._sandbox, *args, **kwargs)

        return bound


class Sandbox(SandboxHandle):
    """Sandbox object with bound service clients.

    This object exposes sandbox metadata directly and provides bound service
    handles so you can call methods like ``sandbox.filesystem.read_file(...)``
    instead of passing the sandbox object into every client call.

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

    def __init__(self, client: object, data: SandboxData | SandboxStatus):
        self._client = client
        self._data: SandboxData | SandboxStatus = data
        self.filesystem = _SandboxServiceProxy(client._filesystem, self)
        self.git = _SandboxServiceProxy(client._git, self)
        self.process = _SandboxServiceProxy(client._process, self)
        self.pty = _SandboxServiceProxy(client._pty, self)
        self.lsp = _SandboxServiceProxy(client._lsp, self)
        self.ssh = _SandboxServiceProxy(client._ssh, self)
        self.code_interpreter = _SandboxServiceProxy(client._code_interpreter, self)
        self.desktop = _SandboxServiceProxy(client._desktop, self)

    def __getattr__(self, name: str) -> object:
        return getattr(self._data, name)

    def __repr__(self) -> str:
        state = getattr(self._data, "state", None)
        return f"Sandbox(id={self.id!r}, state={state!r})"

    def refresh(self) -> Sandbox:
        """Refresh sandbox metadata in place.

        Returns:
            Sandbox: This sandbox object with refreshed metadata.
        """
        latest = self._client.sandboxes.get(self.id)
        self._data = latest._data
        return self

    def pause(self, http_timeout: float | None = None) -> Sandbox:
        """Pause the sandbox and update this handle with the latest metadata.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            Sandbox: This sandbox object with updated metadata.
        """
        latest = self._client.sandboxes.pause(self, http_timeout=http_timeout)
        self._data = latest._data
        return self

    def create_snapshot(
        self,
        *,
        name: str | None = None,
        kill_sandbox_after: bool = False,
        http_timeout: float | None = None,
    ):
        """Create a snapshot from this sandbox.

        Args:
            name: Optional snapshot name. Auto-generated if omitted.
            kill_sandbox_after: Terminate the source sandbox after the snapshot is stored.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            Snapshot: Created snapshot metadata.
        """
        return self._client.sandboxes.create_snapshot(
            self,
            name=name,
            kill_sandbox_after=kill_sandbox_after,
            http_timeout=http_timeout,
        )

    def delete(self, http_timeout: float | None = None) -> None:
        """Delete the sandbox.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._client.sandboxes.delete(self, http_timeout=http_timeout)

    def create_presigned_url(
        self,
        *,
        port: int,
        expires_in: int | None = None,
        http_timeout: float | None = None,
    ) -> PresignedURL:
        """Create a temporary public URL for a specific sandbox port."""
        return self._client.sandboxes.create_presigned_url(
            self,
            port=port,
            expires_in=expires_in,
            http_timeout=http_timeout,
        )

    def delete_presigned_url(self, presigned_url_id: str, http_timeout: float | None = None) -> None:
        """Delete a previously issued presigned URL."""
        self._client.sandboxes.delete_presigned_url(self, presigned_url_id, http_timeout=http_timeout)

    def invoke_url(self, path: str = "/", *, port: int | None = None) -> str:
        """Build an HTTPS URL that routes directly to this sandbox.

        Args:
            path: Request path inside the sandbox application.
            port: Port number for the generated URL.

        Returns:
            str: Sandbox-scoped HTTPS URL.
        """
        return self._client.sandboxes.invoke_url(self, path=path, port=port)

    def websocket_url(self, path: str = "/", *, port: int | None = None) -> str:
        """Build a WSS URL that routes directly to this sandbox.

        Args:
            path: Request path inside the sandbox application.
            port: Port number for the generated URL.

        Returns:
            str: Sandbox-scoped websocket URL.
        """
        return self._client.sandboxes.websocket_url(self, path=path, port=port)

    def get_user_home_dir(self, http_timeout: float | None = None) -> str:
        """Fetch the resolved home directory for the sandbox user."""
        return self._client.sandboxes.get_user_home_dir(self, http_timeout=http_timeout)

    def get_workdir(self, http_timeout: float | None = None) -> str:
        """Fetch the configured working directory for the sandbox."""
        return self._client.sandboxes.get_workdir(self, http_timeout=http_timeout)

    def add_mount(
        self,
        mount: ObjectStorageMountRequestDict,
        http_timeout: float | None = None,
    ) -> ObjectStorageMount:
        """Attach an object storage mount to this sandbox."""
        return self._client.sandboxes.add_mount(self, mount, http_timeout=http_timeout)

    def update_mount(
        self,
        mount_id: str,
        mount: ObjectStorageMountUpdateDict,
        http_timeout: float | None = None,
    ) -> ObjectStorageMount:
        """Update an existing object storage mount on this sandbox."""
        return self._client.sandboxes.update_mount(self, mount_id, mount, http_timeout=http_timeout)

    def delete_mount(self, mount_id: str, http_timeout: float | None = None) -> None:
        """Delete an object storage mount from this sandbox."""
        self._client.sandboxes.delete_mount(self, mount_id, http_timeout=http_timeout)


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


class SandboxesClient(Generic[SandboxT]):
    """Create, inspect, pause, and delete sandboxes.

    Sandboxes are isolated execution environments with their own compute,
    filesystem, and network boundary.

    Attributes:
        None.
    """

    def __init__(
        self,
        transport: Transport,
        *,
        sandbox_domain: str | None = None,
        sandbox_factory: SandboxFactory[SandboxData | SandboxStatus, SandboxT] | None = None,
    ):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None
        self._sandbox_factory = sandbox_factory

    def _wrap_sandbox(self, sandbox: SandboxData | SandboxStatus) -> SandboxT | SandboxData | SandboxStatus:
        if self._sandbox_factory is None:
            return sandbox
        return self._sandbox_factory(sandbox)

    @intercept_errors("Failed to create sandbox: ")
    def create(
        self,
        *,
        template_name: str = DEFAULT_TEMPLATE_NAME,
        vcpu: int = DEFAULT_VCPU,
        memory: int = DEFAULT_MEMORY_MIB,
        timeout: int = DEFAULT_TIMEOUT,
        auto_pause: bool = False,
        otel_export: bool | None = None,
        telemetry: bool | None = None,
        env_vars: dict[str, str] | None = None,
        network_policy: NetworkPolicyDict | None = None,
        mounts: list[ObjectStorageMountRequestDict] | None = None,
        http_timeout: float | None = None,
    ) -> SandboxT | SandboxData | SandboxStatus:
        """Create a new sandbox from a template.

        Args:
            template_name: Name of the template to use.
            vcpu: Number of virtual CPUs (1 to 8).
            memory: Memory in MiB (512 to 8192, must be even).
            timeout: Sandbox timeout in seconds (1 to 28800, default 300).
            auto_pause: Automatically pause the sandbox into a snapshot on timeout.
            otel_export: Inject OpenTelemetry exporter environment into the sandbox.
                Requires ``OTEL_EXPORTER_OTLP_ENDPOINT`` in the local environment and
                also forwards ``OTEL_EXPORTER_OTLP_HEADERS`` when present.
            telemetry: Deprecated alias for ``otel_export``. Use ``otel_export`` instead.
            env_vars: Environment variables to set inside the sandbox.
            network_policy: Outbound network policy for the sandbox.
            mounts: Object storage mounts to attach before boot.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SandboxT | SandboxData | SandboxStatus: Created sandbox object.
        """
        effective_otel_export = otel_export if otel_export is not None else bool(telemetry)

        params = CreateSandboxParams(
            template_name=template_name,
            vcpu=vcpu,
            memory=memory,
            timeout=timeout,
            auto_pause=auto_pause,
            otel_export=effective_otel_export,
            env_vars=_inject_otel_env(env_vars) if effective_otel_export else env_vars,
            network_policy=network_policy,
            mounts=mounts,
        )
        payload = params.to_payload()
        payload.pop("otel_export", None)
        data: SandboxCreateResponseDict = self._transport.request_json(
            "POST", "/v1/sandbox", json=payload, expected_status=201,
            timeout=http_timeout,
        )
        return self._wrap_sandbox(SandboxData.from_dict(data))

    @intercept_errors("Failed to list sandboxes: ")
    def list(
        self,
        *,
        state: str | None = None,
        sort: str = "created_at",
        order_by: str = "desc",
        page: int = 1,
        page_size: int = 20,
        http_timeout: float | None = None,
    ) -> SandboxListResponse:
        """List sandboxes for the authenticated organization.

        Args:
            state: Optional sandbox state filter.
            sort: Sort field, either ``created_at`` or ``state``.
            order_by: Sort direction, either ``asc`` or ``desc``.
            page: 1-based page number.
            page_size: Page size between 1 and 100.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SandboxListResponse: Paginated sandbox summaries.
        """
        valid_states = {"starting", "snapshotting", "running", "paused", "unpausing", "deleting"}
        if state is not None and state not in valid_states:
            raise ValueError(f"state must be one of {sorted(valid_states)}")
        if sort not in {"created_at", "state"}:
            raise ValueError("sort must be one of ['created_at', 'state']")
        if order_by not in {"asc", "desc"}:
            raise ValueError("order_by must be one of ['asc', 'desc']")
        if page < 1:
            raise ValueError("page must be at least 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        params: dict[str, str | int] = {
            "sort": sort,
            "order-by": order_by,
            "page": page,
            "page-size": page_size,
        }
        if state is not None:
            params["state"] = state

        data = cast(ListSandboxesResponseDict, self._transport.request_json(
            "GET",
            "/v1/sandboxes",
            params=params,
            timeout=http_timeout,
        ))
        return SandboxListResponse.from_dict(data)

    @intercept_errors("Failed to pause sandbox: ")
    def pause(self, sandbox: SandboxRef, http_timeout: float | None = None) -> SandboxT | SandboxData | SandboxStatus:
        """Pause a running sandbox.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SandboxT | SandboxData | SandboxStatus: Updated sandbox object.
        """
        data: SandboxCreateResponseDict = self._transport.request_json(
            "POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/pause", expected_status=201,
            timeout=http_timeout,
        )
        return self._wrap_sandbox(SandboxData.from_dict(data))

    @intercept_errors("Failed to create snapshot: ")
    def create_snapshot(
        self,
        sandbox: SandboxRef,
        *,
        name: str | None = None,
        kill_sandbox_after: bool = False,
        http_timeout: float | None = None,
    ) -> Snapshot:
        """Create a snapshot from a running sandbox."""
        payload = CreateSnapshotParams(name=name, kill_sandbox_after=kill_sandbox_after).to_payload()
        data: SnapshotCreateResponseDict = self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/snapshot/create",
            json=payload,
            expected_status=201,
            timeout=http_timeout,
        )
        return Snapshot.from_dict(data)

    @intercept_errors("Failed to get sandbox: ")
    def get(self, sandbox: SandboxRef, http_timeout: float | None = None) -> SandboxT | SandboxData | SandboxStatus:
        """Get the latest sandbox metadata.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SandboxT | SandboxData | SandboxStatus: Current sandbox object.
        """
        data: SandboxStatusResponseDict = self._transport.request_json(
            "GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/",
            timeout=http_timeout,
        )
        return self._wrap_sandbox(SandboxStatus.from_dict(data))

    @intercept_errors("Failed to delete sandbox: ")
    def delete(self, sandbox: SandboxRef, http_timeout: float | None = None) -> None:
        """Terminate and delete a sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
        """
        self._transport.request(
            "DELETE",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/",
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to get sandbox user home directory: ")
    def get_user_home_dir(self, sandbox: SandboxRef, http_timeout: float | None = None) -> str:
        """Get the resolved home directory for the sandbox user.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            str: Resolved sandbox user home directory.
        """
        data = cast(dict[str, object], self._transport.request_json(
            "GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/system/user-home-dir",
            timeout=http_timeout,
        ))
        value = data.get("user_home_dir")
        if not isinstance(value, str):
            raise ValueError("Sandbox user home directory response missing 'user_home_dir'")
        return value

    @intercept_errors("Failed to get sandbox workdir: ")
    def get_workdir(self, sandbox: SandboxRef, http_timeout: float | None = None) -> str:
        """Get the configured working directory for the sandbox.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            str: Configured sandbox workdir.
        """
        data = cast(dict[str, object], self._transport.request_json(
            "GET", f"/v1/sandbox/{sandbox_id_of(sandbox)}/system/workdir",
            timeout=http_timeout,
        ))
        value = data.get("workdir")
        if not isinstance(value, str):
            raise ValueError("Sandbox workdir response missing 'workdir'")
        return value

    @intercept_errors("Failed to create presigned URL: ")
    def create_presigned_url(
        self,
        sandbox: SandboxRef,
        *,
        port: int,
        expires_in: int | None = None,
        http_timeout: float | None = None,
    ) -> PresignedURL:
        params = CreatePresignedURLParams(port=port, expires_in=expires_in)
        data: PresignedURLResponseDict = self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/presigned-url",
            json=params.to_payload(),
            expected_status=201,
            timeout=http_timeout,
        )
        return PresignedURL.from_dict(data)

    @intercept_errors("Failed to delete presigned URL: ")
    def delete_presigned_url(self, sandbox: SandboxRef, presigned_url_id: str, http_timeout: float | None = None) -> None:
        id_value = presigned_url_id.strip()
        if not id_value:
            raise ValueError("presigned_url_id must be a non-empty string")
        self._transport.request(
            "DELETE",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/presigned-url/{id_value}",
            expected_status=204,
            timeout=http_timeout,
        )

    @intercept_errors("Failed to add sandbox mount: ")
    def add_mount(
        self,
        sandbox: SandboxRef,
        mount: ObjectStorageMountRequestDict,
        http_timeout: float | None = None,
    ) -> ObjectStorageMount:
        normalized_mounts = CreateSandboxParams(mounts=[mount]).mounts
        if normalized_mounts is None:
            raise ValueError("mount is required")
        data = cast(dict[str, object], self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/mounts",
            json=normalized_mounts[0],
            expected_status=201,
            timeout=http_timeout,
        ))
        return ObjectStorageMount.from_dict(cast(ObjectStorageMountDict, data))

    @intercept_errors("Failed to update sandbox mount: ")
    def update_mount(
        self,
        sandbox: SandboxRef,
        mount_id: str,
        mount: ObjectStorageMountUpdateDict,
        http_timeout: float | None = None,
    ) -> ObjectStorageMount:
        mount_id_value = mount_id.strip()
        if not mount_id_value:
            raise ValueError("mount_id must be a non-empty string")
        data = cast(dict[str, object], self._transport.request_json(
            "PATCH",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/mounts/{mount_id_value}",
            json=_validate_object_storage_mount_update(mount),
            timeout=http_timeout,
        ))
        return ObjectStorageMount.from_dict(cast(ObjectStorageMountDict, data))

    @intercept_errors("Failed to delete sandbox mount: ")
    def delete_mount(self, sandbox: SandboxRef, mount_id: str, http_timeout: float | None = None) -> None:
        mount_id_value = mount_id.strip()
        if not mount_id_value:
            raise ValueError("mount_id must be a non-empty string")
        self._transport.request(
            "DELETE",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/mounts/{mount_id_value}",
            expected_status=204,
            timeout=http_timeout,
        )

    def invoke_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build an HTTPS URL that routes directly to the sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            port: Port number for the generated URL.
        
        Returns:
            object: Result returned by this operation.
        """
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain, port=port)}{ensure_leading_slash(path)}"

    def websocket_url(self, sandbox: SandboxRef, path: str = "/", *, port: int | None = None) -> str:
        """Build a WSS URL that routes directly to the sandbox.
        
        Args:
            sandbox: Sandbox ID or object.
            path: Path used by this operation.
            port: Port number for the generated URL.
        
        Returns:
            object: Result returned by this operation.
        """
        return websocket_url_from_http(self.invoke_url(sandbox, path, port=port))




__all__ = ["Sandbox", "SandboxesClient"]
