from __future__ import annotations

from typing import Any, Literal, TypedDict, cast

class DesktopDisplayInfoDict(TypedDict, total=False):
    """Wire schema for desktop display information."""
    display: str
    width: int
    height: int

class DesktopWindowDict(TypedDict, total=False):
    """Wire schema for one desktop window."""
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
    """Wire schema for desktop window listings."""
    items: list[DesktopWindowDict]

class DesktopPointerPositionDict(TypedDict, total=False):
    """Wire schema for pointer position."""
    x: int
    y: int

class DesktopRecordingStatusDict(TypedDict, total=False):
    """Wire schema for recording status."""
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
    """Wire schema for recording summary metadata."""
    id: str
    file_name: str
    download: str
    mime_type: str
    size_bytes: int
    created_at: str
    active: bool

class DesktopHealthDict(TypedDict, total=False):
    """Wire schema for desktop health state."""
    ok: bool

class DesktopProcessStatusDict(TypedDict, total=False):
    """Wire schema for one desktop process status."""
    name: str
    running: bool
    pid: int
    stdout_log: str
    stderr_log: str

class DesktopProcessStatusListDict(TypedDict, total=False):
    """Wire schema for desktop process status listings."""
    status: str
    items: list[DesktopProcessStatusDict]
    running: int
    total: int

class DesktopProcessRestartDict(TypedDict, total=False):
    """Wire schema for process restart responses."""
    message: str
    status: DesktopProcessStatusDict

class DesktopProcessLogsDict(TypedDict, total=False):
    """Wire schema for process logs."""
    process: str
    logs: str

class DesktopProcessErrorsDict(TypedDict, total=False):
    """Wire schema for process errors."""
    process: str
    errors: str
