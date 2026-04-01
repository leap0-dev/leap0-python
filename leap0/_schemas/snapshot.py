from __future__ import annotations

from typing import TypedDict

class SnapshotCreateResponseDict(TypedDict, total=False):
    """Wire schema for snapshot creation responses."""
    snapshot_id: str
    name: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    created_at: str
    network_policy: NetworkPolicyDict | None
