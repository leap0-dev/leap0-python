from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class LspSuccessResponseDict(TypedDict, total=False):
    success: bool


@dataclass(slots=True)
class LspResponse:
    success: bool = False

    @classmethod
    def from_dict(cls, data: LspSuccessResponseDict) -> LspResponse:
        return cls(success=bool(data.get("success", False)))
