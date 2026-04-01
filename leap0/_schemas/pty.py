from __future__ import annotations

from typing import TypedDict

class PtySessionInfoDict(TypedDict, total=False):
    """Wire schema for PTY session metadata."""
    id: str
    cwd: str
    envs: dict[str, str]
    cols: int
    rows: int
    created_at: str
    active: bool
    lazy_start: bool

class PtyListResponseDict(TypedDict, total=False):
    """Wire schema for PTY session listings."""
    items: list[PtySessionInfoDict]
