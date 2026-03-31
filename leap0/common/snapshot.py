from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

from .sandbox import NetworkPolicyDict, SandboxState, _parse_sandbox_state


class SnapshotCreateResponseDict(TypedDict, total=False):
    snapshot_id: str
    name: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    created_at: str
    network_policy: NetworkPolicyDict | None


@dataclass(slots=True)
class Snapshot:
    snapshot_id: str
    name: str
    template_id: str = ""
    vcpu: int = 0
    memory_mib: int = 0
    disk_mib: int = 0
    state: SandboxState | str = SandboxState.STARTING
    network_policy: NetworkPolicyDict | None = None
    created_at: str = ""

    @property
    def id(self) -> str:
        return self.snapshot_id

    @classmethod
    def from_dict(cls, data: SnapshotCreateResponseDict) -> Snapshot:
        return cls(
            snapshot_id=data.get("snapshot_id", ""),
            name=data.get("name", ""),
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=_parse_sandbox_state(data.get("state")),
            network_policy=data.get("network_policy"),
            created_at=data.get("created_at", ""),
        )


SnapshotRef = str | Snapshot


def snapshot_id_of(value: SnapshotRef) -> str:
    if isinstance(value, str):
        return value
    return value.snapshot_id
