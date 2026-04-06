from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, ConfigDict, model_validator

from .._schemas.snapshot import SnapshotCreateResponseDict
from .sandbox import NetworkPolicyDict, NetworkPolicyMode, SandboxState, _parse_sandbox_state

class CreateSnapshotParams(BaseModel):
    """Validated snapshot creation parameters."""
    model_config = ConfigDict(extra="forbid")

    name: str | None = None

    @model_validator(mode="after")
    def _validate_name(self) -> CreateSnapshotParams:
        if self.name is not None:
            name = self.name.strip()
            if not name:
                raise ValueError("name must be a non-empty string when provided")
            if len(name) > 64:
                raise ValueError("name must be at most 64 characters")
            self.name = name
        return self

    def to_payload(self) -> dict[str, str]:
        """Convert this object to an API request payload."""
        if self.name is None:
            return {}
        return {"name": self.name}

class ResumeSnapshotParams(BaseModel):
    """Validated snapshot resume parameters."""
    model_config = ConfigDict(extra="forbid")

    snapshot_name: str
    auto_pause: bool = False
    timeout_min: int | None = None
    network_policy: NetworkPolicyDict | None = None

    @model_validator(mode="after")
    def _validate_values(self) -> ResumeSnapshotParams:
        snapshot_name = self.snapshot_name.strip()
        if not snapshot_name:
            raise ValueError("snapshot_name must be a non-empty string")
        if len(snapshot_name) > 64:
            raise ValueError("snapshot_name must be at most 64 characters")
        if self.timeout_min is not None and not 1 <= self.timeout_min <= 480:
            raise ValueError("timeout_min must be between 1 and 480 when provided")
        self.snapshot_name = snapshot_name
        return self

    def to_payload(self) -> dict[str, object]:
        """Convert this object to an API request payload."""
        payload = self.model_dump(exclude_none=True)
        payload["snapshot_name"] = self.snapshot_name
        return payload


CreateSnapshotParams.model_rebuild(_types_namespace={"NetworkPolicyMode": NetworkPolicyMode})
ResumeSnapshotParams.model_rebuild(_types_namespace={"NetworkPolicyMode": NetworkPolicyMode})

@dataclass(slots=True)
class Snapshot:
    """Snapshot metadata returned by the API."""
    id: str
    name: str
    template_id: str = ""
    vcpu: int = 0
    memory_mib: int = 0
    disk_mib: int = 0
    state: SandboxState | str | None = None
    network_policy: NetworkPolicyDict | None = None
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: SnapshotCreateResponseDict) -> Snapshot:
        """Build an instance from a wire-format dictionary."""
        snapshot_id = data.get("id")
        if not isinstance(snapshot_id, str) or not snapshot_id.strip():
            raise ValueError(f"Snapshot response missing required non-empty string 'id', got: {snapshot_id!r}")
        snapshot_name = data.get("name")
        if not isinstance(snapshot_name, str) or not snapshot_name.strip():
            raise ValueError(
                f"Snapshot response missing required non-empty string 'name', got: {snapshot_name!r}"
            )
        state = data.get("state")
        return cls(
            id=snapshot_id,
            name=snapshot_name,
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=_parse_sandbox_state(state) if state is not None else None,
            network_policy=data.get("network_policy"),
            created_at=data.get("created_at", ""),
        )

class SnapshotIdentifiable(Protocol):
    """Protocol for objects exposing a snapshot ID."""
    id: str


SnapshotRef = str | SnapshotIdentifiable

def snapshot_id_of(value: SnapshotRef) -> str:
    """Return the snapshot ID for a snapshot reference."""
    if isinstance(value, str):
        return value
    return value.id
