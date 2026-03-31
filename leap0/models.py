from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any, Literal, cast

from websockets.sync.client import ClientConnection

from ._types import (
    CodeContextDict,
    CodeExecutionOutputDict,
    CodeExecutionResultDict,
    EditFileResponseDict,
    EditResultDict,
    ExecutionErrorDict,
    ExecutionLogsDict,
    FileInfoDict,
    GitCommitResponseDict,
    GitResultDict,
    ImageConfigDict,
    LsResponseDict,
    LspSuccessResponseDict,
    NetworkPolicyDict,
    ProcessResultDict,
    PtySessionInfoDict,
    SandboxCreateResponseDict,
    SandboxState,
    SandboxStatusResponseDict,
    SearchMatchDict,
    SnapshotCreateResponseDict,
    SshAccessValidationDict,
    SshCreateAccessDict,
    StreamEventDict,
    TreeEntryDict,
    TreeResponseDict,
    UploadTemplateResponseDict,
    DesktopDisplayInfoDict,
    DesktopHealthDict,
    DesktopProcessErrorsDict,
    DesktopProcessLogsDict,
    DesktopProcessRestartDict,
    DesktopProcessStatusDict,
    DesktopProcessStatusListDict,
    DesktopPointerPositionDict,
    DesktopRecordingStatusDict,
    DesktopRecordingSummaryDict,
    DesktopWindowDict,
)


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


@dataclass(slots=True)
class Snapshot:
    snapshot_id: str
    name: str
    template_id: str = ""
    vcpu: int = 0
    memory_mib: int = 0
    disk_mib: int = 0
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
            network_policy=data.get("network_policy"),
            created_at=data.get("created_at", ""),
        )


SnapshotRef = str | Snapshot


def snapshot_id_of(value: SnapshotRef) -> str:
    if isinstance(value, str):
        return value
    return value.snapshot_id


@dataclass(slots=True)
class FileInfo:
    name: str
    path: str
    is_dir: bool = False
    size: int = 0
    mode: str = ""
    mtime: int = 0
    owner: str = ""
    group: str = ""
    is_symlink: bool = False
    link_target: str = ""

    @classmethod
    def from_dict(cls, data: FileInfoDict) -> FileInfo:
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            is_dir=bool(data.get("is_dir", False)),
            size=int(data.get("size", 0)),
            mode=data.get("mode", ""),
            mtime=int(data.get("mtime", 0)),
            owner=data.get("owner", ""),
            group=data.get("group", ""),
            is_symlink=bool(data.get("is_symlink", False)),
            link_target=data.get("link_target", ""),
        )


@dataclass(slots=True)
class LsResult:
    items: list[FileInfo]

    @classmethod
    def from_dict(cls, data: LsResponseDict) -> LsResult:
        return cls(items=[FileInfo.from_dict(item) for item in data.get("items", [])])


@dataclass(slots=True)
class FileEdit:
    find: str
    replace: str = ""

    def to_dict(self) -> dict[str, str]:
        return {"find": self.find, "replace": self.replace}


@dataclass(slots=True)
class EditFileResult:
    diff: str = ""
    replacements: int = 0

    @classmethod
    def from_dict(cls, data: EditFileResponseDict) -> EditFileResult:
        return cls(
            diff=data.get("diff", ""),
            replacements=int(data.get("replacements", 0)),
        )


@dataclass(slots=True)
class EditResult:
    file: str = ""
    success: bool = False
    error: str = ""

    @classmethod
    def from_dict(cls, data: EditResultDict) -> EditResult:
        return cls(
            file=data.get("file", ""),
            success=bool(data.get("success", False)),
            error=data.get("error", ""),
        )


@dataclass(slots=True)
class SearchMatch:
    path: str = ""
    line: int = 0
    content: str = ""

    @classmethod
    def from_dict(cls, data: SearchMatchDict) -> SearchMatch:
        return cls(
            path=data.get("path", ""),
            line=int(data.get("line", 0)),
            content=data.get("content", ""),
        )


@dataclass(slots=True)
class TreeEntry:
    name: str
    type: str = "file"
    children: list[TreeEntry] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: TreeEntryDict) -> TreeEntry:
        return cls(
            name=data.get("name", ""),
            type=data.get("type", "file"),
            children=[TreeEntry.from_dict(c) for c in data.get("children", [])],
        )


@dataclass(slots=True)
class TreeResult:
    items: list[TreeEntry]

    @classmethod
    def from_dict(cls, data: TreeResponseDict) -> TreeResult:
        return cls(items=[TreeEntry.from_dict(item) for item in data.get("items", [])])


@dataclass(slots=True)
class GitResult:
    output: str
    exit_code: int

    @classmethod
    def from_dict(cls, data: GitResultDict) -> GitResult:
        return cls(output=data.get("output", ""), exit_code=int(data.get("exit_code", 0)))


@dataclass(slots=True)
class GitCommitResult:
    sha: str | None
    result: GitResult | None

    @classmethod
    def from_dict(cls, data: GitCommitResponseDict) -> GitCommitResult:
        result_data = data.get("result")
        return cls(
            sha=data.get("sha"),
            result=GitResult.from_dict(result_data) if isinstance(result_data, dict) else None,
        )


@dataclass(slots=True)
class ProcessResult:
    exit_code: int
    result: str

    @classmethod
    def from_dict(cls, data: ProcessResultDict) -> ProcessResult:
        return cls(exit_code=int(data.get("exit_code", 0)), result=data.get("result", ""))


@dataclass(slots=True)
class SshAccess:
    id: str
    password: str
    ssh_command: str
    sandbox_id: str = ""
    expires_at: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: SshCreateAccessDict) -> SshAccess:
        return cls(
            id=data.get("id", ""),
            password=data.get("password", ""),
            ssh_command=data.get("ssh_command", ""),
            sandbox_id=data.get("sandbox_id", ""),
            expires_at=data.get("expires_at", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass(slots=True)
class SshValidation:
    valid: bool
    sandbox_id: str

    @classmethod
    def from_dict(cls, data: SshAccessValidationDict) -> SshValidation:
        return cls(
            valid=bool(data.get("valid", False)),
            sandbox_id=data.get("sandbox_id", ""),
        )


@dataclass(slots=True)
class PtySession:
    id: str = ""
    cwd: str = ""
    envs: dict[str, str] = field(default_factory=dict)
    cols: int = 0
    rows: int = 0
    created_at: str = ""
    active: bool = False
    lazy_start: bool = False

    @classmethod
    def from_dict(cls, data: PtySessionInfoDict) -> PtySession:
        return cls(
            id=data.get("id", data.get("session_id", "")),
            cwd=data.get("cwd", ""),
            envs=data.get("envs") or {},
            cols=int(data.get("cols", 0)),
            rows=int(data.get("rows", 0)),
            created_at=data.get("created_at", ""),
            active=bool(data.get("active", False)),
            lazy_start=bool(data.get("lazy_start", False)),
        )


@dataclass(slots=True)
class PtyConnection:
    websocket: ClientConnection

    def send(self, data: str | bytes) -> None:
        payload = data.encode() if isinstance(data, str) else data
        self.websocket.send(payload)

    def recv(self) -> bytes:
        message = self.websocket.recv()
        if isinstance(message, str):
            return message.encode()
        if isinstance(message, bytes):
            return message
        return b"".join(message)

    def close(self) -> None:
        self.websocket.close()


@dataclass(slots=True)
class LspResponse:
    success: bool = False

    @classmethod
    def from_dict(cls, data: LspSuccessResponseDict) -> LspResponse:
        return cls(success=bool(data.get("success", False)))


@dataclass(slots=True)
class ImageConfig:
    entrypoint: list[str] = field(default_factory=list)
    cmd: list[str] = field(default_factory=list)
    working_dir: str | None = None
    user: str = ""
    env: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: ImageConfigDict) -> ImageConfig:
        return cls(
            entrypoint=data.get("entrypoint") or [],
            cmd=data.get("cmd") or [],
            working_dir=data.get("working_dir"),
            user=data.get("user", ""),
            env=data.get("env"),
        )


@dataclass(slots=True)
class Template:
    id: str
    name: str
    digest: str = ""
    image_config: ImageConfig | None = None
    is_system: bool = False
    created_at: str = ""

    @classmethod
    def from_dict(cls, data: UploadTemplateResponseDict) -> Template:
        ic = data.get("image_config")
        return cls(
            id=data.get("id", ""),  # type: ignore[arg-type]
            name=data.get("name", ""),  # type: ignore[arg-type]
            digest=data.get("digest", ""),  # type: ignore[arg-type]
            image_config=ImageConfig.from_dict(ic) if isinstance(ic, dict) else None,
            is_system=bool(data.get("is_system", False)),  # type: ignore[arg-type]
            created_at=data.get("created_at", ""),  # type: ignore[arg-type]
        )


_LANGUAGE_INT_TO_STR: dict[int, str] = {1: "python", 2: "typescript"}


def _normalize_language(value: int | str | None) -> str:
    """Accept both the server's integer enum (1=python, 2=typescript) and plain strings."""
    if isinstance(value, int):
        return _LANGUAGE_INT_TO_STR.get(value, str(value))
    return str(value) if value else ""


@dataclass(slots=True)
class CodeExecutionOutput:
    is_primary: bool = False
    text: str | None = None
    png: str | None = None
    svg: str | None = None
    html: str | None = None
    markdown: str | None = None
    json_data: dict[str, Any] | None = None
    jpeg: str | None = None
    pdf: str | None = None
    latex: str | None = None
    javascript: str | None = None
    extra: dict[str, Any] | None = None

    @classmethod
    def from_dict(cls, data: CodeExecutionOutputDict) -> CodeExecutionOutput:
        return cls(
            is_primary=bool(data.get("is_primary", data.get("is_main_result", False))),
            text=data.get("text"),
            png=data.get("png"),
            svg=data.get("svg"),
            html=data.get("html"),
            markdown=data.get("markdown"),
            json_data=data.get("json"),
            jpeg=data.get("jpeg"),
            pdf=data.get("pdf"),
            latex=data.get("latex"),
            javascript=data.get("javascript"),
            extra=data.get("extra"),
        )

    @property
    def is_main_result(self) -> bool:
        return self.is_primary

    def png_bytes(self) -> bytes | None:
        return base64.b64decode(self.png) if self.png else None

    def jpeg_bytes(self) -> bytes | None:
        return base64.b64decode(self.jpeg) if self.jpeg else None

    def pdf_bytes(self) -> bytes | None:
        return base64.b64decode(self.pdf) if self.pdf else None


@dataclass(slots=True)
class CodeExecutionError:
    name: str
    value: str
    traceback: str

    @classmethod
    def from_dict(cls, data: ExecutionErrorDict) -> CodeExecutionError:
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            traceback=data.get("traceback", ""),
        )


@dataclass(slots=True)
class ExecutionLogs:
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: ExecutionLogsDict) -> ExecutionLogs:
        return cls(
            stdout=data.get("stdout") or [],
            stderr=data.get("stderr") or [],
        )


@dataclass(slots=True)
class CodeExecutionResult:
    items: list[CodeExecutionOutput]
    logs: ExecutionLogs
    error: CodeExecutionError | None
    execution_count: int | None
    context_id: str | None = None

    @classmethod
    def from_dict(cls, data: CodeExecutionResultDict, *, context_id: str | None = None) -> CodeExecutionResult:
        error = data.get("error")
        logs_data = data.get("logs", {})
        return cls(
            items=[CodeExecutionOutput.from_dict(item) for item in data.get("items", [])],
            logs=ExecutionLogs.from_dict(logs_data) if logs_data else ExecutionLogs(),  # type: ignore[arg-type]
            error=CodeExecutionError.from_dict(error) if isinstance(error, dict) else None,
            execution_count=data.get("execution_count"),
            context_id=context_id,
        )

    @property
    def main_text(self) -> str | None:
        for result in self.items:
            if result.is_primary:
                return result.text
        return self.items[-1].text if self.items else None


_STREAM_TYPE_INT_TO_STR: dict[int, str] = {0: "stdout", 1: "stderr", 2: "exit", 3: "error"}

StreamEventType = Literal["stdout", "stderr", "exit", "error"]


@dataclass(slots=True)
class StreamEvent:
    type: str
    data: str = ""
    code: int | None = None

    @classmethod
    def from_dict(cls, data: StreamEventDict) -> StreamEvent:
        raw_type = data.get("type", "")
        if isinstance(raw_type, int):
            event_type = _STREAM_TYPE_INT_TO_STR.get(raw_type, str(raw_type))
        else:
            event_type = str(raw_type)
        return cls(
            type=event_type,
            data=data.get("data", ""),
            code=data.get("code"),
        )


@dataclass(slots=True)
class CodeContext:
    id: str
    language: str = ""
    cwd: str = ""

    @classmethod
    def from_dict(cls, data: CodeContextDict) -> CodeContext:
        return cls(
            id=data.get("id", data.get("context_id", "")),
            language=_normalize_language(data.get("language")),
            cwd=data.get("cwd", ""),
        )


@dataclass(slots=True)
class DesktopDisplayInfo:
    display: str = ""
    width: int = 0
    height: int = 0

    @classmethod
    def from_dict(cls, data: DesktopDisplayInfoDict) -> DesktopDisplayInfo:
        return cls(
            display=data.get("display", ""),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
        )


@dataclass(slots=True)
class DesktopWindow:
    id: str = ""
    desktop: int = 0
    pid: int = 0
    x: int = 0
    y: int = 0
    width: int = 0
    height: int = 0
    window_class: str = ""
    host: str = ""
    title: str = ""
    focused: bool = False

    @classmethod
    def from_dict(cls, data: DesktopWindowDict) -> DesktopWindow:
        return cls(
            id=data.get("id", ""),
            desktop=int(data.get("desktop", 0)),
            pid=int(data.get("pid", 0)),
            x=int(data.get("x", 0)),
            y=int(data.get("y", 0)),
            width=int(data.get("width", 0)),
            height=int(data.get("height", 0)),
            window_class=data.get("class", data.get("class_", "")),
            host=data.get("host", ""),
            title=data.get("title", ""),
            focused=bool(data.get("focused", False)),
        )


@dataclass(slots=True)
class DesktopPointerPosition:
    x: int = 0
    y: int = 0

    @classmethod
    def from_dict(cls, data: DesktopPointerPositionDict) -> DesktopPointerPosition:
        return cls(x=int(data.get("x", 0)), y=int(data.get("y", 0)))


@dataclass(slots=True)
class DesktopRecordingStatus:
    id: str = ""
    active: bool = False
    path: str = ""
    started_at: str = ""
    stopped_at: str = ""
    download: str = ""
    mime_type: str = ""
    file_name: str = ""
    display: str = ""
    resolution: str = ""

    @classmethod
    def from_dict(cls, data: DesktopRecordingStatusDict) -> DesktopRecordingStatus:
        return cls(
            id=data.get("id", ""),
            active=bool(data.get("active", False)),
            path=data.get("path", ""),
            started_at=data.get("started_at", ""),
            stopped_at=data.get("stopped_at", ""),
            download=data.get("download", ""),
            mime_type=data.get("mime_type", ""),
            file_name=data.get("file_name", ""),
            display=data.get("display", ""),
            resolution=data.get("resolution", ""),
        )


@dataclass(slots=True)
class DesktopRecordingSummary:
    id: str = ""
    file_name: str = ""
    path: str = ""
    download: str = ""
    mime_type: str = ""
    size_bytes: int = 0
    created_at: str = ""
    active: bool = False

    @classmethod
    def from_dict(cls, data: DesktopRecordingSummaryDict) -> DesktopRecordingSummary:
        return cls(
            id=data.get("id", ""),
            file_name=data.get("file_name", ""),
            path=data.get("path", ""),
            download=data.get("download", ""),
            mime_type=data.get("mime_type", ""),
            size_bytes=int(data.get("size_bytes", 0)),
            created_at=data.get("created_at", ""),
            active=bool(data.get("active", False)),
        )


@dataclass(slots=True)
class DesktopHealth:
    ok: bool = False
    state: str = ""

    @classmethod
    def from_dict(cls, data: DesktopHealthDict) -> DesktopHealth:
        return cls(ok=bool(data.get("ok", False)), state=data.get("state", ""))


@dataclass(slots=True)
class DesktopProcessStatus:
    name: str = ""
    running: bool = False
    pid: int = 0
    stdout_log: str = ""
    stderr_log: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessStatusDict) -> DesktopProcessStatus:
        return cls(
            name=data.get("name", ""),
            running=bool(data.get("running", False)),
            pid=int(data.get("pid", 0)),
            stdout_log=data.get("stdout_log", ""),
            stderr_log=data.get("stderr_log", ""),
        )


@dataclass(slots=True)
class DesktopProcessStatusList:
    status: str = ""
    items: list[DesktopProcessStatus] = field(default_factory=list)
    running: int = 0
    total: int = 0

    @classmethod
    def from_dict(cls, data: DesktopProcessStatusListDict) -> DesktopProcessStatusList:
        return cls(
            status=data.get("status", ""),
            items=[DesktopProcessStatus.from_dict(cast(DesktopProcessStatusDict, cast(object, item))) for item in data.get("items", [])],
            running=int(data.get("running", 0)),
            total=int(data.get("total", 0)),
        )


@dataclass(slots=True)
class DesktopProcessRestart:
    message: str = ""
    status: DesktopProcessStatus | None = None

    @classmethod
    def from_dict(cls, data: DesktopProcessRestartDict) -> DesktopProcessRestart:
        status = data.get("status")
        return cls(
            message=data.get("message", ""),
            status=DesktopProcessStatus.from_dict(cast(DesktopProcessStatusDict, cast(object, status))) if isinstance(status, dict) else None,
        )


@dataclass(slots=True)
class DesktopProcessLogs:
    process: str = ""
    logs: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessLogsDict) -> DesktopProcessLogs:
        return cls(process=data.get("process", ""), logs=data.get("logs", ""))


@dataclass(slots=True)
class DesktopProcessErrors:
    process: str = ""
    errors: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessErrorsDict) -> DesktopProcessErrors:
        return cls(process=data.get("process", ""), errors=data.get("errors", ""))
