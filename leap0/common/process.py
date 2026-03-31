from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class ProcessResultDict(TypedDict, total=False):
    exit_code: int
    result: str


@dataclass(slots=True)
class ProcessResult:
    exit_code: int
    result: str

    @classmethod
    def from_dict(cls, data: ProcessResultDict) -> ProcessResult:
        return cls(exit_code=int(data.get("exit_code", 0)), result=data.get("result", ""))
