from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, TypedDict, cast


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
    download: str
    mime_type: str
    size_bytes: int
    created_at: str
    active: bool


class DesktopHealthDict(TypedDict, total=False):
    ok: bool


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
            download=data.get("download", ""),
            mime_type=data.get("mime_type", ""),
            size_bytes=int(data.get("size_bytes", 0)),
            created_at=data.get("created_at", ""),
            active=bool(data.get("active", False)),
        )


@dataclass(slots=True)
class DesktopHealth:
    ok: bool = False

    @classmethod
    def from_dict(cls, data: DesktopHealthDict) -> DesktopHealth:
        return cls(ok=bool(data.get("ok", False)))


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
