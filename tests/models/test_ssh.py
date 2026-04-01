from __future__ import annotations

from leap0.models.ssh import SshAccess, SshValidation


class TestSshAccess:
    def test_from_dict(self):
        s = SshAccess.from_dict({"id": "ssh-1", "password": "secret", "ssh_command": "ssh user@host",
                                 "sandbox_id": "sbx-1", "expires_at": "2025-12-31",
                                 "created_at": "2025-01-01", "updated_at": "2025-01-01"})
        assert s.id == "ssh-1"
        assert s.password == "secret"


class TestSshValidation:
    def test_from_dict(self):
        v = SshValidation.from_dict({"valid": True, "sandbox_id": "sbx-1"})
        assert v.valid is True

    def test_empty_dict(self):
        assert SshValidation.from_dict({}).valid is False
