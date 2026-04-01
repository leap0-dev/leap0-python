from __future__ import annotations

from typing import TypedDict

class ProcessResultDict(TypedDict, total=False):
    """Wire schema for process execution results."""
    exit_code: int
    result: str
