from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypedDict

from typing_extensions import NotRequired, Required


class SandboxState(str, Enum):
    STARTING = "starting"
    SNAPSHOTTING = "snapshotting"
    RUNNING = "running"
    PAUSED = "paused"
    UNPAUSING = "unpausing"
    DELETING = "deleting"
    DELETED = "deleted"


class NetworkPolicyMode(str, Enum):
    ALLOW_ALL = "allow-all"
    DENY_ALL = "deny-all"
    CUSTOM = "custom"


class TransformRuleDict(TypedDict, total=False):
    domain: Required[str]
    inject_headers: NotRequired[dict[str, str]]
    strip_headers: NotRequired[list[str]]


class NetworkPolicyDict(TypedDict, total=False):
    mode: Required[NetworkPolicyMode | str]
    allow_domains: NotRequired[list[str]]
    allow_cidrs: NotRequired[list[str]]
    transforms: NotRequired[list[TransformRuleDict]]


class SandboxCreateResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str
    network_policy: NetworkPolicyDict | None


class SandboxStatusResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str


@dataclass(slots=True)
class Sandbox:
    id: str
    template_id: str = ""
    vcpu: int = 0
    memory_mib: int = 0
    disk_mib: int = 0
    state: SandboxState | str = SandboxState.STARTING
    auto_pause: bool = False
    created_at: str = ""
    network_policy: NetworkPolicyDict | None = None

    @classmethod
    def from_dict(cls, data: SandboxCreateResponseDict) -> Sandbox:
        sandbox_id = data.get("id")
        if not sandbox_id or not isinstance(sandbox_id, str):
            raise ValueError(f"Sandbox response missing required non-empty string 'id', got: {sandbox_id!r}")
        state = _parse_sandbox_state(data.get("state"))
        return cls(
            id=sandbox_id,
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=state,
            auto_pause=bool(data.get("auto_pause", False)),
            created_at=data.get("created_at", ""),
            network_policy=data.get("network_policy"),
        )


@dataclass(slots=True)
class SandboxStatus:
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str

    @classmethod
    def from_dict(cls, data: SandboxStatusResponseDict) -> SandboxStatus:
        state = _parse_sandbox_state(data.get("state"))
        return cls(
            id=data.get("id", ""),
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=state,
            auto_pause=bool(data.get("auto_pause", False)),
            created_at=data.get("created_at", ""),
        )


SandboxRef = str | Sandbox | SandboxStatus


def _parse_sandbox_state(value: SandboxState | str | None) -> SandboxState | str:
    if value is None:
        return SandboxState.STARTING
    try:
        return SandboxState(value)
    except ValueError:
        return str(value)


def sandbox_id_of(value: SandboxRef) -> str:
    if isinstance(value, str):
        return value
    return value.id
