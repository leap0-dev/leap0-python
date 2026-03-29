from __future__ import annotations

from ._transport import Transport
from .models import SandboxRef, SshAccess, SshValidation, sandbox_id_of


class SshClient:
    """Manage SSH access credentials for a sandbox.

    Each sandbox supports a single set of SSH credentials at a time. Creating
    access when credentials already exist returns 409 Conflict. Use
    :meth:`regenerate_access` to rotate credentials without revoking first.
    """

    def __init__(self, transport: Transport):
        self._transport = transport

    def create_access(self, sandbox: SandboxRef) -> SshAccess:
        """Generate SSH credentials for a sandbox.

        Returns an access ID (used as the SSH username), a password, and the
        full SSH command to connect.
        """
        data = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/access", expected_status=201)
        return SshAccess.from_dict(data)  # type: ignore[arg-type]

    def delete_access(self, sandbox: SandboxRef) -> None:
        """Revoke SSH access for a sandbox. The credential is invalidated immediately."""
        self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/access", expected_status=204)

    def validate_access(self, sandbox: SandboxRef, *, access_id: str, password: str) -> SshValidation:
        """Check whether an SSH access credential is still valid and not expired."""
        data = self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/validate",
            json={"id": access_id, "password": password},
        )
        return SshValidation.from_dict(data)  # type: ignore[arg-type]

    def regenerate_access(self, sandbox: SandboxRef) -> SshAccess:
        """Invalidate the current credential and generate a new one. The expiry is also reset."""
        data = self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/regen")
        return SshAccess.from_dict(data)  # type: ignore[arg-type]
