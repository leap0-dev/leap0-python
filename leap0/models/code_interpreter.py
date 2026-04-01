from __future__ import annotations

import base64
import binascii
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from .._schemas.code_interpreter import CodeContextDict, CodeExecutionOutputDict, CodeExecutionResultDict, ExecutionErrorDict, ExecutionLogsDict, ListContextsResponseDict, StreamEventDict

_logger = logging.getLogger(__name__)

def _decode_base64(data: str | None, label: str) -> bytes | None:
    """Decode a base64 string, returning ``None`` on missing/invalid input."""
    if not data:
        return None
    try:
        return base64.b64decode(data)
    except (binascii.Error, ValueError):
        _logger.debug("Failed to decode %s base64 data", label)
        return None

class CodeLanguage(str, Enum):
    """Supported code interpreter languages."""
    PYTHON = "python"
    TYPESCRIPT = "typescript"

class StreamEventType(str, Enum):
    """Supported code interpreter stream event types."""
    STDOUT = "stdout"
    STDERR = "stderr"
    EXIT = "exit"
    ERROR = "error"

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
    """Single output item produced by a code execution.

    Attributes:
        is_primary: Whether this item is the primary result.
        text: Plain-text output.
        png: Base64-encoded PNG payload.
        svg: SVG payload.
        html: HTML payload.
        markdown: Markdown payload.
        json_data: Structured JSON payload.
        jpeg: Base64-encoded JPEG payload.
        pdf: Base64-encoded PDF payload.
        latex: LaTeX payload.
        javascript: JavaScript payload.
        extra: Additional provider-specific data.
    """
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
        """Build an execution output object from a wire-format dictionary.

        Args:
            data: Output payload returned by the API.

        Returns:
            CodeExecutionOutput: Parsed execution output.
        """
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
        """Return whether this output item is the primary result."""
        return self.is_primary

    def png_bytes(self) -> bytes | None:
        """Return the PNG payload as decoded bytes when present."""
        return _decode_base64(self.png, "png")

    def jpeg_bytes(self) -> bytes | None:
        """Return the JPEG payload as decoded bytes when present."""
        return _decode_base64(self.jpeg, "jpeg")

    def pdf_bytes(self) -> bytes | None:
        """Return the PDF payload as decoded bytes when present."""
        return _decode_base64(self.pdf, "pdf")

@dataclass(slots=True)
class CodeExecutionError:
    """Structured code execution error details."""
    name: str
    value: str
    traceback: str

    @classmethod
    def from_dict(cls, data: ExecutionErrorDict) -> CodeExecutionError:
        """Build an instance from a wire-format dictionary."""
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            traceback=data.get("traceback", ""),
        )

@dataclass(slots=True)
class ExecutionLogs:
    """Captured stdout and stderr logs from code execution."""
    stdout: list[str] = field(default_factory=list)
    stderr: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: ExecutionLogsDict) -> ExecutionLogs:
        """Build an instance from a wire-format dictionary."""
        return cls(
            stdout=data.get("stdout") or [],
            stderr=data.get("stderr") or [],
        )

@dataclass(slots=True)
class CodeExecutionResult:
    """Full result of a code execution request.

    Attributes:
        items: Output items produced by the execution.
        logs: Captured stdout and stderr logs.
        error: Structured execution error, if any.
        execution_count: Execution counter when provided by the runtime.
        context_id: Context identifier associated with the execution.
    """
    items: list[CodeExecutionOutput]
    logs: ExecutionLogs
    error: CodeExecutionError | None
    execution_count: int | None
    context_id: str | None = None

    @classmethod
    def from_dict(cls, data: CodeExecutionResultDict) -> CodeExecutionResult:
        """Build an execution result from a wire-format dictionary.

        Args:
            data: Execution result payload returned by the API.

        Returns:
            CodeExecutionResult: Parsed execution result.
        """
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
        """Return the primary text result when available.

        Returns:
            str | None: Primary textual output, or ``None`` if no primary text result exists.
        """
        for result in self.items:
            if result.is_primary:
                return result.text
        return self.items[-1].text if self.items else None

_STREAM_TYPE_INT_TO_STR: dict[int, str] = {0: "stdout", 1: "stderr", 2: "exit", 3: "error"}

@dataclass(slots=True)
class StreamEvent:
    """Single streamed event from code execution."""
    type: StreamEventType | str
    data: str = ""
    code: int | None = None

    @classmethod
    def from_dict(cls, data: StreamEventDict) -> StreamEvent:
        """Build an instance from a wire-format dictionary."""
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
    """Persistent code execution context."""
    id: str
    language: CodeLanguage | str = ""
    cwd: str = ""

    @classmethod
    def from_dict(cls, data: CodeContextDict) -> CodeContext:
        """Build an instance from a wire-format dictionary."""
        return cls(
            id=data.get("id", ""),
            language=_normalize_language(data.get("language")),
            cwd=data.get("cwd", ""),
        )
