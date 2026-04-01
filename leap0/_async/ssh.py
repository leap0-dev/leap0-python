from __future__ import annotations

from typing import cast

from ._transport import AsyncTransport
from .._utils.errors import intercept_errors
from ..models.sandbox import SandboxRef, sandbox_id_of
from ..models.ssh import SshAccess, SshValidation


class AsyncSshClient:
    """Manage SSH access credentials for a sandbox.
    
        Each sandbox supports a single set of SSH credentials at a time. Creating
        access when credentials already exist returns 409 Conflict. Use
        :meth:`regenerate_access` to rotate credentials without revoking first.
    
        Example:
            ```python
            sandbox = client.sandboxes.create()
            access = sandbox.ssh.create_access()
            print(access.command)
            ```
        
    Attributes:
        None.
    """

    def __init__(self, transport: AsyncTransport):
        self._transport = transport

    @intercept_errors("Failed to create SSH access: ")
    async def create_access(self, sandbox: SandboxRef, http_timeout: float | None = None) -> SshAccess:
        """Generate SSH credentials for a sandbox.

        Returns an access ID (used as the SSH username), a password, and the
        full SSH command to connect.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SshAccess: Generated SSH credential bundle.
        """
        data = await self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/access", expected_status=201, timeout=http_timeout)
        return SshAccess.from_dict(cast(dict, data))

    @intercept_errors("Failed to delete SSH access: ")
    async def delete_access(self, sandbox: SandboxRef, http_timeout: float | None = None) -> None:
        """Revoke SSH access for a sandbox. The credential is invalidated immediately.

        Args:
            sandbox: Sandbox ID or object.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        await self._transport.request("DELETE", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/access", expected_status=204, timeout=http_timeout)

    @intercept_errors("Failed to validate SSH access: ")
    async def validate_access(self, sandbox: SandboxRef, *, access_id: str, password: str, http_timeout: float | None = None) -> SshValidation:
        """Check whether an SSH access credential is still valid and not expired.

        Args:
            sandbox: Sandbox ID or object.
            access_id: SSH access identifier.
            password: SSH password.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.

        Returns:
            SshValidation: Validation result for the supplied credential pair.
        """
        data = await self._transport.request_json(
            "POST",
            f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/validate",
            json={"id": access_id, "password": password},
            timeout=http_timeout,
        )
        return SshValidation.from_dict(cast(dict, data))

    @intercept_errors("Failed to regenerate SSH access: ")
    async def regenerate_access(self, sandbox: SandboxRef, http_timeout: float | None = None) -> SshAccess:
        """Invalidate the current credential and generate a new one. The expiry is also reset.
        
                Args:
                    sandbox: Sandbox ID or object.
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = await self._transport.request_json("POST", f"/v1/sandbox/{sandbox_id_of(sandbox)}/ssh/regen", timeout=http_timeout)
        return SshAccess.from_dict(cast(dict, data))
