from __future__ import annotations

from typing import Protocol, TypeAlias, TypeVar

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonObject: TypeAlias = dict[str, JsonValue]
BinaryFiles: TypeAlias = list[tuple[str, bytes]]

SandboxModelT = TypeVar("SandboxModelT")
SandboxReturnT = TypeVar("SandboxReturnT")


class SandboxFactory(Protocol[SandboxModelT, SandboxReturnT]):
    """Protocol for factory callables that wrap sandbox models."""
    def __call__(self, data: SandboxModelT) -> SandboxReturnT: ...


class SandboxHandle:
    """Nominal base type for SDK sandbox references."""

    id: str


class SyncSandboxService(Protocol):
    """Protocol for sandbox-bound synchronous service callables."""
    def __call__(self, sandbox: object, *args: object, **kwargs: object) -> object: ...


class AsyncSandboxService(Protocol):
    """Protocol for sandbox-bound asynchronous service callables."""
    async def __call__(self, sandbox: object, *args: object, **kwargs: object) -> object: ...


class HeaderMapping(Protocol):
    """Protocol for mutable HTTP header mappings."""

    def update(self, other: dict[str, str]) -> None:
        """Update the mapping with another header dictionary."""
        ...
