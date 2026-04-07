from __future__ import annotations

from dataclasses import dataclass
from .._schemas.process import ProcessResultDict

@dataclass(slots=True)
class ProcessResult:
    """Result of a one-shot process execution."""
    exit_code: int
    stdout: str
    stderr: str

    @classmethod
    def from_dict(cls, data: ProcessResultDict) -> ProcessResult:
        """Build an instance from a wire-format dictionary."""
        return cls(
            exit_code=int(data.get("exit_code", 0)),
            stdout=data.get("stdout") if isinstance(data.get("stdout"), str) else "",
            stderr=data.get("stderr") if isinstance(data.get("stderr"), str) else "",
        )
