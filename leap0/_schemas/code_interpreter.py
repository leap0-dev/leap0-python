from __future__ import annotations

from typing import Any, TypedDict

class CodeExecutionOutputDict(TypedDict, total=False):
    """Wire schema for one execution output item."""
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
    """Wire schema for structured execution errors."""
    name: str
    value: str
    traceback: str

class ExecutionLogsDict(TypedDict, total=False):
    """Wire schema for execution logs."""
    stdout: list[str]
    stderr: list[str]

class CodeExecutionResultDict(TypedDict, total=False):
    """Wire schema for a full execution result."""
    context_id: str
    items: list[CodeExecutionOutputDict]
    logs: ExecutionLogsDict
    error: ExecutionErrorDict | None
    execution_count: int | None

class StreamEventDict(TypedDict, total=False):
    """Wire schema for a streamed execution event."""
    type: int | str
    data: str
    code: int | None

class CodeContextDict(TypedDict, total=False):
    """Wire schema for a code execution context."""
    id: str
    language: int | str
    cwd: str

class ListContextsResponseDict(TypedDict):
    """Wire schema for listing execution contexts."""
    items: list[CodeContextDict]
