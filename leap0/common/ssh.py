from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict


class SshCreateAccessDict(TypedDict, total=False):
    id: str
    sandbox_id: str
    password: str
    expires_at: str
    created_at: str
    updated_at: str
    ssh_command: str


class SshAccessValidationDict(TypedDict, total=False):
    valid: bool
    sandbox_id: str


@dataclass(slots=True)
class SshAccess:
    id: str
    password: str
    ssh_command: str
    sandbox_id: str = ""
    expires_at: str = ""
    created_at: str = ""
    updated_at: str = ""

    @classmethod
    def from_dict(cls, data: SshCreateAccessDict) -> SshAccess:
        return cls(
            id=data.get("id", ""),
            password=data.get("password", ""),
            ssh_command=data.get("ssh_command", ""),
            sandbox_id=data.get("sandbox_id", ""),
            expires_at=data.get("expires_at", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
        )


@dataclass(slots=True)
class SshValidation:
    valid: bool
    sandbox_id: str

    @classmethod
    def from_dict(cls, data: SshAccessValidationDict) -> SshValidation:
        return cls(
            valid=bool(data.get("valid", False)),
            sandbox_id=data.get("sandbox_id", ""),
        )
