from __future__ import annotations

from typing import TypedDict

class GitResultDict(TypedDict, total=False):
    """Wire schema for a generic Git operation response."""
    output: str
    exit_code: int

class GitCommitResponseDict(TypedDict, total=False):
    """Wire schema for a Git commit response."""
    sha: str | None
    result: GitResultDict | None
