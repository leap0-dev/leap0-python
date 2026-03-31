from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class GitResultDict(TypedDict, total=False):
    output: str
    exit_code: int


class GitCommitResponseDict(TypedDict, total=False):
    sha: str | None
    result: GitResultDict | None


@dataclass(slots=True)
class GitResult:
    output: str
    exit_code: int

    @classmethod
    def from_dict(cls, data: GitResultDict) -> GitResult:
        return cls(output=data.get("output", ""), exit_code=int(data.get("exit_code", 0)))


@dataclass(slots=True)
class GitCommitResult:
    sha: str | None
    result: GitResult | None

    @classmethod
    def from_dict(cls, data: GitCommitResponseDict) -> GitCommitResult:
        result_data = data.get("result")
        return cls(
            sha=data.get("sha"),
            result=GitResult.from_dict(result_data) if isinstance(result_data, dict) else None,
        )
