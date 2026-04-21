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

class ObjectStorageMountRequestDict(TypedDict, total=False):
    """Wire schema for object storage mount requests."""
    type: Required[str]
    bucket: Required[str]
    mount_path: Required[str]
    endpoint: Required[str]
    prefix: str
    read_only: bool
    access_key_id: str
    secret_access_key: str

class ObjectStorageMountUpdateDict(TypedDict, total=False):
    """Wire schema for sandbox mount update requests."""
    bucket: str
    mount_path: str
    endpoint: str
    prefix: str
    read_only: bool
    access_key_id: str
    secret_access_key: str

class ObjectStorageMountDict(TypedDict, total=False):
    """Wire schema for object storage mounts returned by the API."""
    id: Required[str]
    type: Required[str]
    bucket: Required[str]
    mount_path: Required[str]
    prefix: str
    read_only: bool

class SandboxCreateResponseDict(TypedDict, total=False):
    """Wire schema for sandbox creation responses."""
    id: Required[str]
    template_id: str
    mounts: list[ObjectStorageMountDict]
    vcpu: int
    memory: int
    disk: int
    timeout: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str
    network_policy: NetworkPolicyDict | None

class SandboxStatusResponseDict(TypedDict, total=False):
    """Wire schema for sandbox status responses."""
    id: Required[str]
    template_id: str
    mounts: list[ObjectStorageMountDict]
    vcpu: int
    memory: int
    disk: int
    timeout: int
    state: SandboxState | str
    auto_pause: bool
    created_at: str

class SandboxListItemResponseDict(TypedDict, total=False):
    """Wire schema for sandbox list items."""
    id: Required[str]
    template_id: Required[str]
    state: Required[SandboxState | str]
    launch_time: str
    state_change_time: str
    timeout_at: int
    created_at: Required[str]

class ListSandboxesResponseDict(TypedDict):
    """Wire schema for paginated sandbox list responses."""
    items: list[SandboxListItemResponseDict]
    total_items: int


class CreatePresignedURLRequestDict(TypedDict, total=False):
    """Wire schema for presigned URL creation requests."""

    port: Required[int]
    expires_in: int


class PresignedURLResponseDict(TypedDict):
    """Wire schema for presigned URL responses."""

    id: str
    token: str
    url: str
    sandbox_id: str
    port: int
    expires_at: str
    created_at: str
