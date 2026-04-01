from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict
from typing_extensions import NotRequired, Required

if TYPE_CHECKING:
    from ..models.sandbox import NetworkPolicyMode, SandboxState

class TransformRuleDict(TypedDict, total=False):
    """Wire schema for network transform rules."""
    domain: Required[str]
    inject_headers: NotRequired[dict[str, str]]
    strip_headers: NotRequired[list[str]]

class NetworkPolicyDict(TypedDict, total=False):
    """Wire schema for sandbox network policy."""
    mode: Required[NetworkPolicyMode | str]
    allow_domains: NotRequired[list[str]]
    allow_cidrs: NotRequired[list[str]]
    transforms: NotRequired[list[TransformRuleDict]]

class SandboxCreateResponseDict(TypedDict):
    """Wire schema for sandbox creation responses."""
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
    """Wire schema for sandbox status responses."""
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str
