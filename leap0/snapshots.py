from __future__ import annotations

from typing import Any

from ._transport import Transport
from ._utils.errors import intercept_errors
from .common.sandbox import NetworkPolicyDict, Sandbox, SandboxCreateResponseDict, SandboxRef, sandbox_id_of
from .common.snapshot import Snapshot, SnapshotCreateResponseDict, SnapshotRef, snapshot_id_of


class SnapshotsClient:
    """Create, resume, and delete sandbox snapshots.

    A snapshot captures the full state of a running sandbox so it can be
    restored later.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    @intercept_errors("Failed to create snapshot: ")
    def create(
        self,
        sandbox: SandboxRef,
        *,
        name: str | None = None,
    ) -> Snapshot:
        """Create a snapshot of a running sandbox without stopping it.

        Args:
            sandbox: Sandbox ID or object to snapshot.
            name: Optional snapshot name. Auto-generated if omitted.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        data: SnapshotCreateResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/snapshot/create",
            json=payload,
            expected_status=201,
        )
        return Snapshot.from_dict(data)

    @intercept_errors("Failed to pause sandbox: ")
    def pause(
        self,
        sandbox: SandboxRef,
        *,
        name: str | None = None,
    ) -> Snapshot:
        """Pause a running sandbox and create a snapshot in one step.

        The sandbox is stopped after the snapshot is taken.

        Args:
            sandbox: Sandbox ID or object to pause.
            name: Optional snapshot name. Auto-generated if omitted.
        """
        payload: dict[str, Any] = {}
        if name is not None:
            payload["name"] = name
        data: SnapshotCreateResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/snapshot/pause",
            json=payload,
            expected_status=201,
        )
        return Snapshot.from_dict(data)

    @intercept_errors("Failed to resume snapshot: ")
    def resume(
        self,
        *,
        snapshot_name: str,
        auto_pause: bool = False,
        timeout_min: int | None = None,
        network_policy: NetworkPolicyDict | None = None,
    ) -> Sandbox:
        """Restore a sandbox from a snapshot.

        Args:
            snapshot_name: Name of the snapshot to restore.
            auto_pause: Automatically pause the restored sandbox on timeout.
            timeout_min: Sandbox timeout in minutes.
            network_policy: Override the network policy from the snapshot.
        """
        payload: dict[str, Any] = {
            "snapshot_name": snapshot_name,
            "auto_pause": auto_pause,
        }
        if timeout_min is not None:
            payload["timeout_min"] = timeout_min
        if network_policy is not None:
            payload["network_policy"] = network_policy
        data: SandboxCreateResponseDict = self._transport.request_json(  # type: ignore[assignment]
            "POST",
            "/v1/snapshot/resume",
            json=payload,
            expected_status=201,
        )
        return Sandbox.from_dict(data)

    @intercept_errors("Failed to delete snapshot: ")
    def delete(self, snapshot: SnapshotRef) -> None:
        """Delete a snapshot."""
        self._transport.request("DELETE", f"/v1/snapshot/{snapshot_id_of(snapshot)}", expected_status=204)
