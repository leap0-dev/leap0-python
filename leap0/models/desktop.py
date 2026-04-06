from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, ConfigDict, StrictBool, field_validator, model_validator

from .._schemas.desktop import DesktopDisplayInfoDict, DesktopHealthDict, DesktopPointerPositionDict, DesktopProcessErrorsDict, DesktopProcessLogsDict, DesktopProcessRestartDict, DesktopProcessStatusDict, DesktopProcessStatusListDict, DesktopRecordingStatusDict, DesktopRecordingSummaryDict, DesktopWindowDict, DesktopWindowsDict


class DesktopResizeScreenParams(BaseModel):
    """Validated request payload for resizing the desktop screen."""

    model_config = ConfigDict(extra="forbid")

    width: int
    height: int

    @model_validator(mode="after")
    def _validate_bounds(self) -> "DesktopResizeScreenParams":
        if not 320 <= self.width <= 7680:
            raise ValueError("width must be between 320 and 7680")
        if not 320 <= self.height <= 4320:
            raise ValueError("height must be between 320 and 4320")
        return self


class DesktopScreenshotParams(BaseModel):
    """Validated query parameters for desktop screenshots."""

    model_config = ConfigDict(extra="forbid")

    format: str | None = None
    quality: int | None = None
    x: int | None = None
    y: int | None = None
    width: int | None = None
    height: int | None = None

    @model_validator(mode="after")
    def _validate_region(self) -> "DesktopScreenshotParams":
        if self.format is not None and self.format not in {"png", "jpg", "jpeg"}:
            raise ValueError("format must be one of: png, jpg, jpeg")
        if self.quality is not None and not 1 <= self.quality <= 100:
            raise ValueError("quality must be between 1 and 100")
        if (self.width is None) != (self.height is None):
            raise ValueError("width and height must be provided together")
        for name, value in (("x", self.x), ("y", self.y)):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be >= 0")
        for name, value in (("width", self.width), ("height", self.height)):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be >= 0")
        return self


class DesktopScreenshotRegionParams(BaseModel):
    """Validated request payload for region screenshot capture."""

    model_config = ConfigDict(extra="forbid")

    x: int
    y: int
    width: int
    height: int
    format: str | None = None
    quality: int | None = None

    @model_validator(mode="after")
    def _validate_region(self) -> "DesktopScreenshotRegionParams":
        if self.format is not None and self.format not in {"png", "jpg", "jpeg"}:
            raise ValueError("format must be one of: png, jpg, jpeg")
        if self.quality is not None and not 1 <= self.quality <= 100:
            raise ValueError("quality must be between 1 and 100")
        if self.x < 0:
            raise ValueError("x must be >= 0")
        if self.y < 0:
            raise ValueError("y must be >= 0")
        if self.width < 1:
            raise ValueError("width must be >= 1")
        if self.height < 1:
            raise ValueError("height must be >= 1")
        return self


class DesktopClickParams(BaseModel):
    """Validated request payload for desktop click operations."""

    model_config = ConfigDict(extra="forbid")

    x: int | None = None
    y: int | None = None
    button: int | None = None

    @model_validator(mode="after")
    def _validate_click(self) -> "DesktopClickParams":
        if (self.x is None) != (self.y is None):
            raise ValueError("x and y must be provided together or both omitted")
        for name, value in (("x", self.x), ("y", self.y)):
            if value is not None and value < 0:
                raise ValueError(f"{name} must be >= 0")
        if self.button is not None and self.button not in {1, 2, 3}:
            raise ValueError("button must be one of: 1, 2, 3")
        return self


class DesktopOkResponse(BaseModel):
    """Validated response shape for desktop endpoints that return ``ok``."""

    model_config = ConfigDict(extra="allow")

    ok: StrictBool

    @field_validator("ok", mode="before")
    @classmethod
    def _validate_ok(cls, value: object) -> object:
        if not isinstance(value, bool):
            raise ValueError(f"Desktop response missing boolean 'ok', got: {value!r}")
        return value


class DesktopStatusStreamErrorEvent(BaseModel):
    """Validated error envelope emitted by the desktop status SSE stream."""

    model_config = ConfigDict(extra="allow")

    error: str | None = None
    message: str | None = None

    @model_validator(mode="after")
    def _validate_error(self) -> "DesktopStatusStreamErrorEvent":
        if self.error is None and self.message is None:
            raise ValueError("Desktop status stream error event must include error or message")
        return self

    @property
    def detail(self) -> str:
        """Return the normalized human-readable error detail."""
        return self.error or self.message or "unknown desktop status stream error"

def _require_str(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if not isinstance(value, str):
        raise ValueError(f"Desktop response missing string '{field}', got: {value!r}")
    return value


def _require_bool(data: dict[str, Any], field: str) -> bool:
    value = data.get(field)
    if not isinstance(value, bool):
        raise ValueError(f"Desktop response missing boolean '{field}', got: {value!r}")
    return value


def _require_int(data: dict[str, Any], field: str) -> int:
    value = data.get(field)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Desktop response missing integer '{field}', got: {value!r}")
    return value


def _optional_int(data: dict[str, Any], field: str) -> int | None:
    value = data.get(field)
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"Desktop response has invalid integer '{field}', got: {value!r}")
    return value

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
            display=_require_str(data, "display"),
            width=_require_int(data, "width"),
            height=_require_int(data, "height"),
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
            desktop=_optional_int(data, "desktop") or 0,
            pid=_optional_int(data, "pid") or 0,
            x=_optional_int(data, "x") or 0,
            y=_optional_int(data, "y") or 0,
            width=_optional_int(data, "width") or 0,
            height=_optional_int(data, "height") or 0,
            window_class=data.get("class", data.get("class_", "")),
            host=data.get("host", ""),
            title=data.get("title", ""),
            focused=_require_bool(data, "focused") if "focused" in data else False,
        )

@dataclass(slots=True)
class DesktopPointerPosition:
    """Mouse pointer position on the desktop."""
    x: int = 0
    y: int = 0

    @classmethod
    def from_dict(cls, data: DesktopPointerPositionDict) -> DesktopPointerPosition:
        """Build an instance from a wire-format dictionary."""
        return cls(x=_require_int(data, "x"), y=_require_int(data, "y"))

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
            size_bytes=_require_int(data, "size_bytes"),
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
        return cls(ok=_require_bool(data, "ok"))

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
            name=_require_str(data, "name"),
            running=_require_bool(data, "running"),
            pid=_optional_int(data, "pid") or 0,
            stdout_log=_require_str(data, "stdout_log"),
            stderr_log=_require_str(data, "stderr_log"),
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
            raise ValueError(f"Desktop response missing array 'items', got: {raw_items!r}")
        return cls(
            status=_require_str(data, "status"),
            items=[
                DesktopProcessStatus.from_dict(item)
                for item in _validated_status_items(raw_items)
            ],
            running=_require_int(data, "running"),
            total=_require_int(data, "total"),
        )


def _validated_status_items(raw_items: list[Any] | tuple[Any, ...]) -> list[DesktopProcessStatusDict]:
    validated_items: list[DesktopProcessStatusDict] = []
    for index, item in enumerate(raw_items):
        if not isinstance(item, dict):
            raise TypeError(f"Desktop response item at index {index} must be a mapping, got: {item!r}")
        validated_items.append(item)
    return validated_items

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
