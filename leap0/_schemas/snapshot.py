from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from .._schemas.sandbox import NetworkPolicyDict
    from ..models.sandbox import SandboxState

class SnapshotCreateResponseDict(TypedDict, total=False):
    """Wire schema for snapshot creation responses."""
    id: str
    name: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    created_at: str
    network_policy: NetworkPolicyDict | None
