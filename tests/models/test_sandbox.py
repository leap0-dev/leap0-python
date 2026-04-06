from __future__ import annotations

import pytest

from leap0.models.sandbox import CreateSandboxParams, Sandbox, SandboxStatus, _validate_network_policy, sandbox_id_of


class TestSandboxIdOf:
    def test_from_string(self):
        assert sandbox_id_of("sbx-123") == "sbx-123"

    def test_from_sandbox(self):
        assert sandbox_id_of(Sandbox(id="sbx-abc")) == "sbx-abc"

    def test_from_sandbox_status(self):
        s = SandboxStatus(id="sbx-xyz", template_id="t", vcpu=1, memory_mib=512,
                          disk_mib=10240, state="running", auto_pause=False, created_at="")
        assert sandbox_id_of(s) == "sbx-xyz"

    def test_rejects_unrelated_object_with_id(self):
        class FakeSandbox:
            id = "sbx-fake"

        with pytest.raises(TypeError, match="sandbox must be"):
            sandbox_id_of(FakeSandbox())


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
        with pytest.raises(ValueError, match="missing required non-empty string 'id'"):
            SandboxStatus.from_dict({})


class TestCreateSandboxParams:
    def test_rejects_invalid_network_policy(self):
        with pytest.raises(ValueError, match=r"network_policy\.mode"):
            CreateSandboxParams(network_policy={"mode": "nope"})

        with pytest.raises(ValueError, match="invalid network policy domain pattern"):
            CreateSandboxParams(network_policy={"mode": "custom", "allow_domains": ["localhost"]})

        with pytest.raises(ValueError, match="invalid network policy CIDR"):
            CreateSandboxParams(network_policy={"mode": "custom", "allow_cidrs": ["bad"]})

        with pytest.raises(ValueError, match="allow_domains must contain at most 50"):
            CreateSandboxParams(network_policy={"mode": "custom", "allow_domains": ["a.example.com"] * 51})

        with pytest.raises(ValueError, match=r"transforms\[0\] missing required 'domain'"):
            _validate_network_policy({"mode": "custom", "transforms": [{"rewrite": "x"}]})

        with pytest.raises(ValueError, match=r"transforms\[0\] must be a mapping"):
            _validate_network_policy({"mode": "custom", "transforms": ["bad"]})
