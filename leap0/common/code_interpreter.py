from __future__ import annotations

import base64
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypedDict


class CodeLanguage(str, Enum):
    PYTHON = "python"
    TYPESCRIPT = "typescript"


class StreamEventType(str, Enum):
    STDOUT = "stdout"
    STDERR = "stderr"
    EXIT = "exit"
    ERROR = "error"


class CodeExecutionOutputDict(TypedDict, total=False):
    is_primary: bool
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
    context_id: str
    items: list[CodeExecutionOutputDict]
    logs: ExecutionLogsDict
    error: ExecutionErrorDict | None
    execution_count: int | None


class StreamEventDict(TypedDict, total=False):
    type: int | str
    data: str
    code: int | None


class CodeContextDict(TypedDict, total=False):
    id: str
    language: int | str
    cwd: str


class ListContextsResponseDict(TypedDict):
    items: list[CodeContextDict]


_LANGUAGE_INT_TO_STR: dict[int, str] = {1: "python", 2: "typescript"}


def _normalize_language(value: int | str | None) -> CodeLanguage | str:
    if isinstance(value, int):
        value = _LANGUAGE_INT_TO_STR.get(value, str(value))
    if not value:
        return ""
    try:
        return CodeLanguage(str(value))
    except ValueError:
        return str(value)


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
            is_primary=bool(data.get("is_primary", False)),
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
    def from_dict(cls, data: CodeExecutionResultDict) -> CodeExecutionResult:
        error = data.get("error")
        logs_data = data.get("logs", {})
        return cls(
            items=[CodeExecutionOutput.from_dict(item) for item in data.get("items", [])],
            logs=ExecutionLogs.from_dict(logs_data) if logs_data else ExecutionLogs(),  # type: ignore[arg-type]
            error=CodeExecutionError.from_dict(error) if isinstance(error, dict) else None,
            execution_count=data.get("execution_count"),
            context_id=data.get("context_id"),
        )

    @property
    def main_text(self) -> str | None:
        for result in self.items:
            if result.is_primary:
                return result.text
        return self.items[-1].text if self.items else None


_STREAM_TYPE_INT_TO_STR: dict[int, str] = {0: "stdout", 1: "stderr", 2: "exit", 3: "error"}

@dataclass(slots=True)
class StreamEvent:
    type: StreamEventType | str
    data: str = ""
    code: int | None = None

    @classmethod
    def from_dict(cls, data: StreamEventDict) -> StreamEvent:
        raw_type = data.get("type", "")
        if isinstance(raw_type, int):
            event_type = _STREAM_TYPE_INT_TO_STR.get(raw_type, str(raw_type))
        else:
            event_type = str(raw_type)
        try:
            parsed_type: StreamEventType | str = StreamEventType(event_type)
        except ValueError:
            parsed_type = event_type
        return cls(
            type=parsed_type,
            data=data.get("data", ""),
            code=data.get("code"),
        )


@dataclass(slots=True)
class CodeContext:
    id: str
    language: CodeLanguage | str = ""
    cwd: str = ""

    @classmethod
    def from_dict(cls, data: CodeContextDict) -> CodeContext:
        return cls(
            id=data.get("id", ""),
            language=_normalize_language(data.get("language")),
            cwd=data.get("cwd", ""),
        )
