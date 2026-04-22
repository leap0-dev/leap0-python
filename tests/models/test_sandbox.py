from __future__ import annotations

import pytest
from pydantic import ValidationError

from leap0.models.sandbox import CreatePresignedURLParams, CreateSandboxParams, ObjectStorageMount, PresignedURL, Sandbox, SandboxStatus, _validate_network_policy, _validate_object_storage_mount_update, sandbox_id_of


class TestSandboxIdOf:
    def test_from_string(self):
        assert sandbox_id_of("sbx-123") == "sbx-123"

    def test_from_sandbox(self):
        assert sandbox_id_of(Sandbox(id="sbx-abc")) == "sbx-abc"

    def test_from_sandbox_status(self):
        s = SandboxStatus(id="sbx-xyz", template_id="t", vcpu=1, memory=512,
                          disk=10240, timeout=300, state="running", auto_pause=False, created_at="")
        assert sandbox_id_of(s) == "sbx-xyz"

    def test_rejects_unrelated_object_with_id(self):
        class FakeSandbox:
            id = "sbx-fake"

        with pytest.raises(TypeError, match="sandbox must be"):
            sandbox_id_of(FakeSandbox())


class TestSandbox:
    def test_full_dict(self):
        s = Sandbox.from_dict({"id": "sbx-1", "template_id": "tpl-1", "vcpu": 2, "memory": 2048,
                                "disk": 10240, "timeout": 300, "state": "running", "auto_pause": True,
                               "created_at": "2025-01-01", "network_policy": {"mode": "allow-all"},
                               "mounts": [{"id": "mnt-1", "type": "object-storage", "bucket": "project-assets", "mount_path": "/data/assets", "prefix": "docs/", "read_only": True}]})
        assert s.id == "sbx-1"
        assert s.vcpu == 2
        assert s.state == "running"
        assert s.network_policy == {"mode": "allow-all"}
        assert s.mounts == [ObjectStorageMount(id="mnt-1", type="object-storage", bucket="project-assets", mount_path="/data/assets", prefix="docs/", read_only=True)]

    def test_minimal_dict(self):
        s = Sandbox.from_dict({"id": "sbx-2"})
        assert s.id == "sbx-2"
        assert s.state == "starting"
        assert s.network_policy is None
        assert s.mounts is None


class TestSandboxStatus:
    def test_full_dict(self):
        s = SandboxStatus.from_dict({"id": "sbx-1", "template_id": "tpl-1", "vcpu": 4, "memory": 4096,
                                     "disk": 10240, "timeout": 300, "state": "paused", "auto_pause": True, "created_at": "2025-01-01",
                                     "mounts": [{"id": "mnt-1", "type": "object-storage", "bucket": "project-assets", "mount_path": "/data/assets", "prefix": "docs/", "read_only": True}]})
        assert s.state == "paused"
        assert s.vcpu == 4
        assert s.mounts == [ObjectStorageMount(id="mnt-1", type="object-storage", bucket="project-assets", mount_path="/data/assets", prefix="docs/", read_only=True)]

    def test_empty_dict_raises(self):
        with pytest.raises(ValueError, match="missing required non-empty string 'id'"):
            SandboxStatus.from_dict({})

    def test_absent_mounts_preserved_as_none(self):
        s = SandboxStatus.from_dict({"id": "sbx-2", "template_id": "tpl-1", "vcpu": 1,
                                     "memory": 512, "disk": 10240, "timeout": 300,
                                     "state": "running", "auto_pause": False, "created_at": "2025-01-01"})
        assert s.mounts is None


class TestCreateSandboxParams:
    def test_accepts_object_storage_mounts(self):
        params = CreateSandboxParams(mounts=[{
            "type": "object-storage",
            "bucket": "project-assets",
            "mount_path": "/data/assets",
            "endpoint": "https://storage.example.com",
            "prefix": "docs/",
        }])

        assert params.mounts == [{
            "type": "object-storage",
            "bucket": "project-assets",
            "mount_path": "/data/assets",
            "endpoint": "https://storage.example.com",
            "prefix": "docs/",
        }]

    def test_preserves_empty_mount_credentials(self):
        params = CreateSandboxParams(mounts=[{
            "type": "object-storage",
            "bucket": "project-assets",
            "mount_path": "/data/assets",
            "endpoint": "https://storage.example.com",
            "access_key_id": "",
            "secret_access_key": "",
        }])

        assert params.mounts == [{
            "type": "object-storage",
            "bucket": "project-assets",
            "mount_path": "/data/assets",
            "endpoint": "https://storage.example.com",
            "access_key_id": "",
            "secret_access_key": "",
        }]

    def test_rejects_invalid_mounts(self):
        with pytest.raises(ValueError, match=r"mounts\[0\]\.type"):
            CreateSandboxParams(mounts=[{"type": "other", "bucket": "b", "mount_path": "/data", "endpoint": "https://storage.example.com"}])

        with pytest.raises(ValueError, match=r"mounts\[0\]\.endpoint must be a valid URL"):
            CreateSandboxParams(mounts=[{"type": "object-storage", "bucket": "b", "mount_path": "/data", "endpoint": "not-a-url"}])

        with pytest.raises(ValueError, match=r"mounts\[0\]\.prefix must be relative, must not contain '\.\.', and must end with '/'"):
            CreateSandboxParams(mounts=[{"type": "object-storage", "bucket": "b", "mount_path": "/data", "endpoint": "https://storage.example.com", "prefix": ""}])

        with pytest.raises(ValueError, match=r"mounts\[0\]\.prefix"):
            CreateSandboxParams(mounts=[{"type": "object-storage", "bucket": "b", "mount_path": "/data", "endpoint": "https://storage.example.com", "prefix": "/bad"}])

        with pytest.raises(ValueError, match=r"mounts\[1\]\.mount_path must be unique"):
            CreateSandboxParams(mounts=[
                {"type": "object-storage", "bucket": "a", "mount_path": "/data", "endpoint": "https://storage-a.example.com"},
                {"type": "object-storage", "bucket": "b", "mount_path": "/data", "endpoint": "https://storage-b.example.com"},
            ])

    def test_rejects_empty_mount_update(self):
        with pytest.raises(ValueError, match="at least one field"):
            _validate_object_storage_mount_update({})

    def test_rejects_invalid_mount_update_endpoint(self):
        with pytest.raises(ValueError, match="endpoint must be a valid URL"):
            _validate_object_storage_mount_update({"endpoint": "not-a-url"})

    def test_rejects_empty_mount_update_prefix(self):
        with pytest.raises(ValueError, match=r"prefix must be relative, must not contain '\.\.', and must end with '/'"):
            _validate_object_storage_mount_update({"prefix": ""})

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


class TestCreatePresignedURLParams:
    def test_rejects_invalid_values(self):
        with pytest.raises(ValidationError, match="port"):
            CreatePresignedURLParams(port=0)

        with pytest.raises(ValidationError, match="expires_in"):
            CreatePresignedURLParams(port=8080, expires_in=0)


class TestPresignedURL:
    def test_from_dict(self):
        result = PresignedURL.from_dict({
            "id": "psu-1",
            "token": "tok_1",
            "url": "https://tok_1.leap0.app",
            "sandbox_id": "sbx_1",
            "port": 8080,
            "expires_at": "2026-01-01T00:15:00Z",
            "created_at": "2026-01-01T00:00:00Z",
        })

        assert result.id == "psu-1"
        assert result.url == "https://tok_1.leap0.app"
        assert result.port == 8080

    def test_from_dict_rejects_missing_timestamps(self):
        with pytest.raises(ValueError, match="timestamp"):
            PresignedURL.from_dict({
                "id": "psu-1",
                "token": "tok_1",
                "url": "https://tok_1.leap0.app",
                "sandbox_id": "sbx_1",
                "port": 8080,
                "expires_at": "",
            })

    def test_from_dict_rejects_invalid_port(self):
        with pytest.raises(ValueError, match=r"invalid 'port'.*0"):
            PresignedURL.from_dict({
                "id": "psu-1",
                "token": "tok_1",
                "url": "https://tok_1.leap0.app",
                "sandbox_id": "sbx_1",
                "port": 0,
                "expires_at": "2026-01-01T00:15:00Z",
                "created_at": "2026-01-01T00:00:00Z",
            })

    def test_repr_redacts_sensitive_fields(self):
        result = PresignedURL.from_dict({
            "id": "psu-1",
            "token": "tok_1",
            "url": "https://tok_1.leap0.app",
            "sandbox_id": "sbx_1",
            "port": 8080,
            "expires_at": "2026-01-01T00:15:00Z",
            "created_at": "2026-01-01T00:00:00Z",
        })

        rendered = repr(result)
        assert "tok_1" not in rendered
        assert "https://tok_1.leap0.app" not in rendered
        assert "<redacted>" in rendered
