from __future__ import annotations

from typing import TypedDict

class SshCreateAccessDict(TypedDict, total=False):
    """Wire schema for SSH access creation responses."""
    id: str
    sandbox_id: str
    password: str
    expires_at: str
    created_at: str
    updated_at: str
    ssh_command: str

class SshAccessValidationDict(TypedDict, total=False):
    """Wire schema for SSH validation responses."""
    valid: bool
    sandbox_id: str
