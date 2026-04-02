from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel, ConfigDict, model_validator

from .._internal.types import SandboxHandle
from .._internal.types import JsonObject
from .._schemas.sandbox import NetworkPolicyDict, SandboxCreateResponseDict, SandboxStatusResponseDict, TransformRuleDict
from .config import DEFAULT_MEMORY_MIB, DEFAULT_TEMPLATE_NAME, DEFAULT_TIMEOUT_MIN, DEFAULT_VCPU

class SandboxState(str, Enum):
    """Lifecycle states for a sandbox."""
    STARTING = "starting"
    SNAPSHOTTING = "snapshotting"
    RUNNING = "running"
    PAUSED = "paused"
    UNPAUSING = "unpausing"
    DELETING = "deleting"
    DELETED = "deleted"

class NetworkPolicyMode(str, Enum):
    """Available outbound network policy modes."""
    ALLOW_ALL = "allow-all"
    DENY_ALL = "deny-all"
    CUSTOM = "custom"

class CreateSandboxParams(BaseModel):
    """Validated sandbox creation parameters."""
    model_config = ConfigDict(extra="forbid")

    template_name: str = DEFAULT_TEMPLATE_NAME
    vcpu: int = DEFAULT_VCPU
    memory_mib: int = DEFAULT_MEMORY_MIB
    timeout_min: int = DEFAULT_TIMEOUT_MIN
    auto_pause: bool = False
    otel_export: bool = False
    env_vars: dict[str, str] | None = None
    network_policy: NetworkPolicyDict | None = None

    @model_validator(mode="after")
    def _validate_values(self) -> CreateSandboxParams:
        template_name = self.template_name.strip()
        if not template_name:
            raise ValueError("template_name must be a non-empty string")
        if len(template_name) > 64:
            raise ValueError("template_name must be at most 64 characters")
        if not 1 <= self.vcpu <= 8:
            raise ValueError("vcpu must be between 1 and 8")
        if self.memory_mib < 512 or self.memory_mib > 8192 or self.memory_mib % 2 != 0:
            raise ValueError("memory_mib must be an even number between 512 and 8192")
        if not 1 <= self.timeout_min <= 480:
            raise ValueError("timeout_min must be between 1 and 480")
        self.template_name = template_name
        return self

    def to_payload(self) -> JsonObject:
        """Convert this object to an API request payload."""
        payload = self.model_dump(exclude_none=True)
        payload["template_name"] = self.template_name.strip()
        return payload


CreateSandboxParams.model_rebuild(_types_namespace={"NetworkPolicyMode": NetworkPolicyMode})

@dataclass(slots=True)
class Sandbox(SandboxHandle):
    """Sandbox model returned by sandbox creation APIs."""
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
        """Build an instance from a wire-format dictionary."""
        sandbox_id = data.get("id")
        if not isinstance(sandbox_id, str) or not sandbox_id.strip():
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
class SandboxStatus(SandboxHandle):
    """Current status snapshot for a sandbox."""
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
        """Build an instance from a wire-format dictionary."""
        sandbox_id = data.get("id")
        if not isinstance(sandbox_id, str) or not sandbox_id.strip():
            raise ValueError(f"SandboxStatus response missing required non-empty string 'id', got: {sandbox_id!r}")
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
        )

SandboxRef: TypeAlias = str | SandboxHandle

def _parse_sandbox_state(value: SandboxState | str | None) -> SandboxState | str:
    if value is None:
        return SandboxState.STARTING
    try:
        return SandboxState(value)
    except ValueError:
        return str(value)

def sandbox_id_of(value: SandboxRef) -> str:
    """Return the sandbox ID for a sandbox reference."""
    if isinstance(value, str):
        return value
    if isinstance(value, SandboxHandle):
        return value.id

    raise TypeError("sandbox must be a sandbox id or SDK sandbox handle")
