from __future__ import annotations

from dataclasses import dataclass
from .._schemas.git import GitCommitResponseDict, GitResultDict

@dataclass(slots=True)
class GitResult:
    """Git command result returned by the SDK."""
    output: str
    exit_code: int

    @classmethod
    def from_dict(cls, data: GitResultDict) -> GitResult:
        """Build an instance from a wire-format dictionary."""
        return cls(output=data.get("output", ""), exit_code=int(data.get("exit_code", 0)))

@dataclass(slots=True)
class GitCommitResult:
    """Git commit result with commit metadata."""
    sha: str | None
    result: GitResult | None

    @classmethod
    def from_dict(cls, data: GitCommitResponseDict) -> GitCommitResult:
        """Build an instance from a wire-format dictionary."""
        result_data = data.get("result")
        return cls(
            sha=data.get("sha"),
            result=GitResult.from_dict(result_data) if isinstance(result_data, dict) else None,
        )
