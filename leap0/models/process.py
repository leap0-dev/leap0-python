from __future__ import annotations

from dataclasses import dataclass, field
from .._schemas.process import ProcessResultDict

@dataclass(slots=True)
class ProcessResult:
    """Result of a one-shot process execution."""
    exit_code: int
    stdout: str
    stderr: str
    _legacy_result: str | dict[str, str] | None = field(default=None, repr=False)

    @property
    def result(self) -> str | dict[str, str]:
        """Backward-compatible alias for legacy result payloads."""
        if self._legacy_result is not None:
            return self._legacy_result
        return self.stdout

    @classmethod
    def from_dict(cls, data: ProcessResultDict) -> ProcessResult:
        """Build an instance from a wire-format dictionary."""
        legacy_result = data.get("result")
        stdout = data.get("stdout")
        stderr = data.get("stderr")

        normalized_legacy_result: str | dict[str, str] | None = None
        if isinstance(legacy_result, dict):
            normalized_legacy_result = {
                key: value
                for key in ("stdout", "stderr")
                if isinstance((value := legacy_result.get(key)), str)
            }
            if stdout is None:
                stdout = legacy_result.get("stdout", "")
            if stderr is None:
                stderr = legacy_result.get("stderr", "")
        elif legacy_result is not None and stdout is None and stderr is None:
            normalized_legacy_result = legacy_result if isinstance(legacy_result, str) else None
            stdout = legacy_result if isinstance(legacy_result, str) else ""
            stderr = ""

        return cls(
            exit_code=int(data.get("exit_code", 0)),
            stdout=stdout if isinstance(stdout, str) else "",
            stderr=stderr if isinstance(stderr, str) else "",
            _legacy_result=normalized_legacy_result,
        )
