from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypedDict

from typing_extensions import NotRequired, Required


SandboxState = Literal["starting", "running", "paused", "unpausing", "deleting", "deleted"]


class TransformRuleDict(TypedDict, total=False):
    domain: Required[str]
    inject_headers: NotRequired[dict[str, str]]
    strip_headers: NotRequired[list[str]]


class NetworkPolicyDict(TypedDict, total=False):
    mode: Required[Literal["allow-all", "deny-all", "custom"]]
    allow_domains: NotRequired[list[str]]
    allow_cidrs: NotRequired[list[str]]
    transforms: NotRequired[list[TransformRuleDict]]


class SandboxCreateResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState
    auto_pause: bool
    created_at: str
    network_policy: NetworkPolicyDict | None


class SandboxStatusResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState
    auto_pause: bool
    created_at: str


@dataclass(slots=True)
class Sandbox:
    id: str
    template_id: str = ""
    vcpu: int = 0
    memory_mib: int = 0
    disk_mib: int = 0
    state: SandboxState = "starting"
    auto_pause: bool = False
    created_at: str = ""
    network_policy: NetworkPolicyDict | None = None

    @classmethod
    def from_dict(cls, data: SandboxCreateResponseDict) -> Sandbox:
        state = data.get("state", "starting")
        return cls(
            id=data["id"],
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=state,  # type: ignore[arg-type]
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
    state: SandboxState
    auto_pause: bool
    created_at: str

    @classmethod
    def from_dict(cls, data: SandboxStatusResponseDict) -> SandboxStatus:
        state = data.get("state", "starting")
        return cls(
            id=data.get("id", ""),
            template_id=data.get("template_id", ""),
            vcpu=int(data.get("vcpu", 0)),
            memory_mib=int(data.get("memory_mib", 0)),
            disk_mib=int(data.get("disk_mib", 0)),
            state=state,  # type: ignore[arg-type]
            auto_pause=bool(data.get("auto_pause", False)),
            created_at=data.get("created_at", ""),
        )


SandboxRef = str | Sandbox | SandboxStatus


def sandbox_id_of(value: SandboxRef) -> str:
    if isinstance(value, str):
        return value
    return value.id
