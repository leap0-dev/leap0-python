from __future__ import annotations

from typing import Any, Literal, TypedDict

from typing_extensions import NotRequired, Required

SandboxState = Literal["starting", "running", "paused", "unpausing", "terminating"]


class SandboxCreateResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState
    auto_pause: bool
    created_at: str
    network_policy: NotRequired[NetworkPolicyDict | None]


class SandboxStatusResponseDict(TypedDict):
    id: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    state: SandboxState
    auto_pause: bool
    created_at: str


class TransformRuleDict(TypedDict, total=False):
    domain: Required[str]
    inject_headers: NotRequired[dict[str, str]]
    strip_headers: NotRequired[list[str]]


class NetworkPolicyDict(TypedDict, total=False):
    mode: Required[Literal["allow-all", "deny-all", "custom"]]
    allow_domains: NotRequired[list[str]]
    allow_cidrs: NotRequired[list[str]]
    transforms: NotRequired[list[TransformRuleDict]]


class SnapshotCreateResponseDict(TypedDict):
    snapshot_id: str
    name: str
    template_id: str
    vcpu: int
    memory_mib: int
    disk_mib: int
    created_at: str
    network_policy: NetworkPolicyDict | None


class FileInfoDict(TypedDict, total=False):
    name: str
    path: str
    is_dir: bool
    size: int
    mode: str
    mtime: int
    owner: str
    group: str
    is_symlink: bool
    link_target: str


class LsResponseDict(TypedDict):
    items: list[FileInfoDict]


class GlobResponseDict(TypedDict):
    items: list[str]


class SearchMatchDict(TypedDict, total=False):
    path: str
    line: int
    content: str


class GrepResponseDict(TypedDict):
    items: list[SearchMatchDict]


class EditFileResponseDict(TypedDict, total=False):
    diff: str
    replacements: int


class EditResultDict(TypedDict, total=False):
    file: str
    success: bool
    error: str


class EditFilesResponseDict(TypedDict):
    items: list[EditResultDict]


class ExistsResponseDict(TypedDict):
    exists: bool


class TreeEntryDict(TypedDict, total=False):
    name: str
    type: str
    children: list[TreeEntryDict]


class TreeResponseDict(TypedDict):
    items: list[TreeEntryDict]


class GitResultDict(TypedDict, total=False):
    output: str
    exit_code: int


class GitCommitResponseDict(TypedDict, total=False):
    sha: str | None
    result: GitResultDict | None


class ProcessResultDict(TypedDict, total=False):
    exit_code: int
    result: str


class SshCreateAccessDict(TypedDict, total=False):
    id: str
    sandbox_id: str
    password: str
    expires_at: str
    created_at: str
    updated_at: str
    ssh_command: str


class SshAccessValidationDict(TypedDict, total=False):
    valid: bool
    sandbox_id: str


class PtyCreateResponseDict(TypedDict, total=False):
    session_id: str


class PtySessionInfoDict(TypedDict, total=False):
    id: str
    session_id: str
    cwd: str
    envs: dict[str, str]
    cols: int
    rows: int
    created_at: str
    active: bool
    lazy_start: bool


class PtyListResponseDict(TypedDict, total=False):
    items: list[PtySessionInfoDict]


class LspSuccessResponseDict(TypedDict, total=False):
    success: bool


RegistryCredentialType = Literal["basic", "aws", "gcp", "azure"]


class RegistryCredentialsDict(TypedDict, total=False):
    type: RegistryCredentialType
    username: str
    password: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    gcp_service_account_json: str
    azure_client_id: str
    azure_client_secret: str
    azure_tenant_id: str


class ImageConfigDict(TypedDict, total=False):
    entrypoint: list[str] | None
    cmd: list[str] | None
    working_dir: str | None
    env: dict[str, Any] | None


class UploadTemplateResponseDict(TypedDict):
    id: str
    name: str
    digest: str
    image_config: ImageConfigDict | None
    is_system: bool
    created_at: str


LanguageLiteral = Literal["python", "typescript"]


class CodeExecutionOutputDict(TypedDict, total=False):
    is_primary: bool
    is_main_result: bool
    text: str | None
    html: str | None
    markdown: str | None
    svg: str | None
    png: str | None
    jpeg: str | None
    pdf: str | None
    latex: str | None
    json: dict[str, Any] | None
    javascript: str | None
    extra: dict[str, Any] | None


class ExecutionErrorDict(TypedDict, total=False):
    name: str
    value: str
    traceback: str


class ExecutionLogsDict(TypedDict, total=False):
    stdout: list[str]
    stderr: list[str]


class CodeExecutionResultDict(TypedDict, total=False):
    items: list[CodeExecutionOutputDict]
    logs: ExecutionLogsDict
    error: ExecutionErrorDict | None
    execution_count: int | None


StreamEventTypeLiteral = Literal["stdout", "stderr", "exit", "error"]


class StreamEventDict(TypedDict, total=False):
    type: int | str
    data: str
    code: int | None


class CodeContextDict(TypedDict, total=False):
    id: str
    context_id: str
    language: int | str
    cwd: str


class ListContextsResponseDict(TypedDict):
    items: list[CodeContextDict]


class DesktopDisplayInfoDict(TypedDict, total=False):
    display: str
    width: int
    height: int


class DesktopWindowDict(TypedDict, total=False):
    id: str
    desktop: int
    pid: int
    x: int
    y: int
    width: int
    height: int
    class_: str
    host: str
    title: str
    focused: bool


class DesktopWindowsDict(TypedDict):
    items: list[DesktopWindowDict]


class DesktopPointerPositionDict(TypedDict, total=False):
    x: int
    y: int


class DesktopRecordingStatusDict(TypedDict, total=False):
    id: str
    active: bool
    path: str
    started_at: str
    stopped_at: str
    download: str
    mime_type: str
    file_name: str
    display: str
    resolution: str


class DesktopRecordingSummaryDict(TypedDict, total=False):
    id: str
    file_name: str
    path: str
    download: str
    mime_type: str
    size_bytes: int
    created_at: str
    active: bool


DesktopHealthState = Literal["starting", "ready", "degraded"]


class DesktopHealthDict(TypedDict, total=False):
    ok: bool
    state: DesktopHealthState


class DesktopProcessStatusDict(TypedDict, total=False):
    name: str
    running: bool
    pid: int
    stdout_log: str
    stderr_log: str


class DesktopProcessStatusListDict(TypedDict, total=False):
    status: str
    items: list[DesktopProcessStatusDict]
    running: int
    total: int


class DesktopProcessRestartDict(TypedDict, total=False):
    message: str
    status: DesktopProcessStatusDict


class DesktopProcessLogsDict(TypedDict, total=False):
    process: str
    logs: str


class DesktopProcessErrorsDict(TypedDict, total=False):
    process: str
    errors: str
