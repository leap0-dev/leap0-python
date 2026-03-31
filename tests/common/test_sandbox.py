from __future__ import annotations

from leap0.common.sandbox import Sandbox, SandboxStatus, sandbox_id_of


class TestSandboxIdOf:
    def test_from_string(self):
        assert sandbox_id_of("sbx-123") == "sbx-123"

    def test_from_sandbox(self):
        assert sandbox_id_of(Sandbox(id="sbx-abc")) == "sbx-abc"

    def test_from_sandbox_status(self):
        s = SandboxStatus(id="sbx-xyz", template_id="t", vcpu=1, memory_mib=512,
                          disk_mib=10240, state="running", auto_pause=False, created_at="")
        assert sandbox_id_of(s) == "sbx-xyz"


class TestSandbox:
    def test_full_dict(self):
        s = Sandbox.from_dict({"id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory_mib": 2048,
                               "disk_mib": 10240, "state": "running", "auto_pause": True,
                               "created_at": "2025-01-01", "network_policy": {"mode": "allow-all"}})
        assert s.id == "sbx-1"
        assert s.vcpu == 2
        assert s.state == "running"
        assert s.network_policy == {"mode": "allow-all"}

    def test_minimal_dict(self):
        s = Sandbox.from_dict({"id": "sbx-2"})
        assert s.id == "sbx-2"
        assert s.state == "starting"
        assert s.network_policy is None


class TestSandboxStatus:
    def test_full_dict(self):
        s = SandboxStatus.from_dict({"id": "sbx-1", "template_id": "tpl-1", "vcpu": 4, "memory_mib": 4096,
                                     "disk_mib": 10240, "state": "paused", "auto_pause": True, "created_at": "2025-01-01"})
        assert s.state == "paused"
        assert s.vcpu == 4

    def test_empty_dict_raises(self):
        import pytest
        with pytest.raises(ValueError, match="missing required non-empty string 'id'"):
            SandboxStatus.from_dict({})
