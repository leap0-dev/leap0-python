from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .._schemas.desktop import DesktopDisplayInfoDict, DesktopHealthDict, DesktopPointerPositionDict, DesktopProcessErrorsDict, DesktopProcessLogsDict, DesktopProcessRestartDict, DesktopProcessStatusDict, DesktopProcessStatusListDict, DesktopRecordingStatusDict, DesktopRecordingSummaryDict, DesktopWindowDict, DesktopWindowsDict

def _safe_int(value: Any, default: int = 0) -> int:
    """Parse *value* as an integer, returning *default* on ``None`` or invalid input."""
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default

@dataclass(slots=True)
class DesktopDisplayInfo:
    """Desktop display geometry information."""
    display: str = ""
    width: int = 0
    height: int = 0

    @classmethod
    def from_dict(cls, data: DesktopDisplayInfoDict) -> DesktopDisplayInfo:
        """Build an instance from a wire-format dictionary."""
        return cls(
            display=data.get("display", ""),
            width=_safe_int(data.get("width"), 0),
            height=_safe_int(data.get("height"), 0),
        )

@dataclass(slots=True)
class DesktopWindow:
    """Single desktop window description."""
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
        """Build an instance from a wire-format dictionary."""
        return cls(
            id=data.get("id", ""),
            desktop=_safe_int(data.get("desktop"), 0),
            pid=_safe_int(data.get("pid"), 0),
            x=_safe_int(data.get("x"), 0),
            y=_safe_int(data.get("y"), 0),
            width=_safe_int(data.get("width"), 0),
            height=_safe_int(data.get("height"), 0),
            window_class=data.get("class", data.get("class_", "")),
            host=data.get("host", ""),
            title=data.get("title", ""),
            focused=bool(data.get("focused", False)),
        )

@dataclass(slots=True)
class DesktopPointerPosition:
    """Mouse pointer position on the desktop."""
    x: int = 0
    y: int = 0

    @classmethod
    def from_dict(cls, data: DesktopPointerPositionDict) -> DesktopPointerPosition:
        """Build an instance from a wire-format dictionary."""
        return cls(x=_safe_int(data.get("x"), 0), y=_safe_int(data.get("y"), 0))

@dataclass(slots=True)
class DesktopRecordingStatus:
    """Desktop recording state and active recording metadata."""
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
        """Build an instance from a wire-format dictionary."""
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
    """Summary metadata for a saved recording."""
    id: str = ""
    file_name: str = ""
    download: str = ""
    mime_type: str = ""
    size_bytes: int = 0
    created_at: str = ""
    active: bool = False

    @classmethod
    def from_dict(cls, data: DesktopRecordingSummaryDict) -> DesktopRecordingSummary:
        """Build an instance from a wire-format dictionary."""
        return cls(
            id=data.get("id", ""),
            file_name=data.get("file_name", ""),
            download=data.get("download", ""),
            mime_type=data.get("mime_type", ""),
            size_bytes=_safe_int(data.get("size_bytes"), 0),
            created_at=data.get("created_at", ""),
            active=bool(data.get("active", False)),
        )

@dataclass(slots=True)
class DesktopHealth:
    """Desktop service health information."""
    ok: bool = False

    @classmethod
    def from_dict(cls, data: DesktopHealthDict) -> DesktopHealth:
        """Build an instance from a wire-format dictionary."""
        return cls(ok=bool(data.get("ok", False)))

@dataclass(slots=True)
class DesktopProcessStatus:
    """Status of one desktop-side process."""
    name: str = ""
    running: bool = False
    pid: int = 0
    stdout_log: str = ""
    stderr_log: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessStatusDict) -> DesktopProcessStatus:
        """Build an instance from a wire-format dictionary."""
        return cls(
            name=data.get("name", ""),
            running=bool(data.get("running", False)),
            pid=_safe_int(data.get("pid"), 0),
            stdout_log=data.get("stdout_log", ""),
            stderr_log=data.get("stderr_log", ""),
        )

@dataclass(slots=True)
class DesktopProcessStatusList:
    """Collection of desktop process statuses."""
    status: str = ""
    items: list[DesktopProcessStatus] = field(default_factory=list)
    running: int = 0
    total: int = 0

    @classmethod
    def from_dict(cls, data: DesktopProcessStatusListDict) -> DesktopProcessStatusList:
        """Build an instance from a wire-format dictionary."""
        raw_items = data.get("items")
        if not isinstance(raw_items, (list, tuple)):
            raw_items = []
        return cls(
            status=data.get("status", ""),
            items=[
                DesktopProcessStatus.from_dict(item)  # type: ignore[arg-type]
                for item in raw_items
                if isinstance(item, dict)
            ],
            running=_safe_int(data.get("running"), 0),
            total=_safe_int(data.get("total"), 0),
        )

@dataclass(slots=True)
class DesktopProcessRestart:
    """Result of restarting a desktop-side process."""
    message: str = ""
    status: DesktopProcessStatus | None = None

    @classmethod
    def from_dict(cls, data: DesktopProcessRestartDict) -> DesktopProcessRestart:
        """Build an instance from a wire-format dictionary."""
        status = data.get("status")
        return cls(
            message=data.get("message", ""),
            status=DesktopProcessStatus.from_dict(status) if isinstance(status, dict) else None,  # type: ignore[arg-type]
        )

@dataclass(slots=True)
class DesktopProcessLogs:
    """Recent logs for a desktop-side process."""
    process: str = ""
    logs: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessLogsDict) -> DesktopProcessLogs:
        """Build an instance from a wire-format dictionary."""
        return cls(process=data.get("process", ""), logs=data.get("logs", ""))

@dataclass(slots=True)
class DesktopProcessErrors:
    """Recent errors for a desktop-side process."""
    process: str = ""
    errors: str = ""

    @classmethod
    def from_dict(cls, data: DesktopProcessErrorsDict) -> DesktopProcessErrors:
        """Build an instance from a wire-format dictionary."""
        return cls(process=data.get("process", ""), errors=data.get("errors", ""))
