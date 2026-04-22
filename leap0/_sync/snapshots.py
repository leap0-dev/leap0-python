from __future__ import annotations

from typing import Generic, TypeVar, cast

from .._internal.types import SandboxFactory
from ..models.sandbox import Sandbox
from ..models.snapshot import RestoreSnapshotParams, Snapshot, SnapshotListResponse, SnapshotRef, snapshot_id_of
from .._schemas.snapshot import ListSnapshotsResponseDict
from .._schemas.sandbox import NetworkPolicyDict, SandboxCreateResponseDict
from .._utils.errors import intercept_errors
from ._transport import Transport

SnapshotSandboxT = TypeVar("SnapshotSandboxT")


class SnapshotsClient(Generic[SnapshotSandboxT]):
    """List, restore, and delete sandbox snapshots.
    
        A snapshot captures the full state of a running sandbox so it can be
        restored later.
    
        Use snapshots when you want a reusable checkpoint of an initialized
        sandbox environment.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport, *, sandbox_factory: SandboxFactory[Sandbox, SnapshotSandboxT] | None = None):
        self._transport = transport
        self._sandbox_factory = sandbox_factory

    def _wrap_sandbox(self, sandbox: Sandbox) -> SnapshotSandboxT | Sandbox:
        if self._sandbox_factory is None:
            return sandbox
        return self._sandbox_factory(sandbox)

    @intercept_errors("Failed to list snapshots: ")
    def list(
        self,
        *,
        query: str = "",
        sort: str = "created_at",
        order_by: str = "desc",
        page: int = 1,
        page_size: int = 20,
        http_timeout: float | None = None,
    ) -> SnapshotListResponse:
        """List snapshots for the authenticated organization."""
        if len(query) > 64:
            raise ValueError("query must be at most 64 characters")
        if sort not in {"created_at", "template_id"}:
            raise ValueError("sort must be one of ['created_at', 'template_id']")
        if order_by not in {"asc", "desc"}:
            raise ValueError("order_by must be one of ['asc', 'desc']")
        if page < 1:
            raise ValueError("page must be at least 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        data = cast(ListSnapshotsResponseDict, self._transport.request_json(
            "GET",
            "/v1/snapshots",
            params={
                "query": query,
                "sort": sort,
                "order-by": order_by,
                "page": page,
                "page-size": page_size,
            },
            timeout=http_timeout,
        ))
        return SnapshotListResponse.from_dict(data)

    @intercept_errors("Failed to restore snapshot: ")
    def restore(
        self,
        *,
        snapshot_name: str,
        auto_pause: bool = False,
        timeout: int | None = None,
        network_policy: NetworkPolicyDict | None = None,
        http_timeout: float | None = None,
    ) -> SnapshotSandboxT | Sandbox:
        """Restore a sandbox from a snapshot.

        Args:
            snapshot_name: Name of the snapshot to restore.
            auto_pause: Automatically pause the restored sandbox on timeout.
            timeout: Sandbox timeout in seconds.
            network_policy: Override the network policy from the snapshot.

            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            Sandbox: Newly restored sandbox.
        """
        payload = RestoreSnapshotParams(
            snapshot_name=snapshot_name,
            auto_pause=auto_pause,
            timeout=timeout,
            network_policy=network_policy,
        ).to_payload()
        data = cast(SandboxCreateResponseDict, self._transport.request_json(
            "POST",
            "/v1/snapshot/restore",
            json=payload,
            expected_status=201,
            timeout=http_timeout,
        ))
        return self._wrap_sandbox(Sandbox.from_dict(data))

    @intercept_errors("Failed to delete snapshot: ")
    def delete(self, snapshot: SnapshotRef, http_timeout: float | None = None) -> None:
        """
                    Delete a snapshot.
        
        Args:
            snapshot: Parameter for this operation.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._transport.request("DELETE", f"/v1/snapshot/{snapshot_id_of(snapshot)}", expected_status=204, timeout=http_timeout)
