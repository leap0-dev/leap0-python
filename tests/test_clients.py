"""Tests for service clients: URL construction and payload building via mock transport."""
from __future__ import annotations

from unittest.mock import MagicMock, call

import httpx
import pytest

from leap0._transport import Transport
from leap0.sandboxes import SandboxesClient
from leap0.snapshots import SnapshotsClient
from leap0.templates import TemplatesClient
from leap0.filesystem import FilesystemClient, _parse_multipart_response
from leap0.git import GitClient
from leap0.process import ProcessClient
from leap0.ssh import SshClient
from leap0.models import FileEdit, Sandbox, Snapshot


def _mock_transport() -> MagicMock:
    t = MagicMock(spec=Transport)
    t.auth_header = "authorization"
    t.auth_value = "Bearer test-key"
    return t


# SandboxesClient

class TestSandboxesClient:
    def test_create_url_and_payload(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "sbx_1", "template_id": "tpl_1", "vcpu": 2, "memory_mib": 2048,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }
        client = SandboxesClient(t, sandbox_domain="sandbox.leap0.dev")
        result = client.create(template_name="my-tpl", vcpu=2, memory_mib=2048)

        t.request_json.assert_called_once()
        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/sandbox"
        assert kwargs["json"]["template_name"] == "my-tpl"
        assert kwargs["json"]["vcpu"] == 2
        assert kwargs["expected_status"] == 201
        assert result.id == "sbx_1"

    def test_get_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "sbx_1", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "running", "auto_pause": False, "created_at": "",
        }
        client = SandboxesClient(t, sandbox_domain="sandbox.leap0.dev")
        client.get("sbx_1")

        args, kwargs = t.request_json.call_args
        assert args[0] == "GET"
        assert args[1] == "/v1/sandbox/sbx_1/"

    def test_delete_url(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = SandboxesClient(t, sandbox_domain="sandbox.leap0.dev")
        client.delete("sbx_1")

        args, kwargs = t.request.call_args
        assert args[0] == "DELETE"
        assert args[1] == "/v1/sandbox/sbx_1/"
        assert kwargs["expected_status"] == 204

    def test_pause_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "sbx_1", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "paused", "auto_pause": False, "created_at": "",
        }
        client = SandboxesClient(t, sandbox_domain="sandbox.leap0.dev")
        client.pause("sbx_1")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/sandbox/sbx_1/pause"

    def test_invoke_url(self):
        client = SandboxesClient(_mock_transport(), sandbox_domain="sandbox.leap0.dev")
        url = client.invoke_url("sbx_1", "/api/health")
        assert url == "https://sbx_1.sandbox.leap0.dev/api/health"

    def test_invoke_url_with_port(self):
        client = SandboxesClient(_mock_transport(), sandbox_domain="sandbox.leap0.dev")
        url = client.invoke_url("sbx_1", "/api", port=3000)
        assert url == "https://3000-sbx_1.sandbox.leap0.dev/api"

    def test_websocket_url(self):
        client = SandboxesClient(_mock_transport(), sandbox_domain="sandbox.leap0.dev")
        url = client.websocket_url("sbx_1", "/ws")
        assert url == "wss://sbx_1.sandbox.leap0.dev/ws"

    def test_accepts_sandbox_object(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "sbx_1", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "running", "auto_pause": False, "created_at": "",
        }
        client = SandboxesClient(t, sandbox_domain="sandbox.leap0.dev")
        sandbox = Sandbox(id="sbx_obj")
        client.get(sandbox)

        args, _ = t.request_json.call_args
        assert "sbx_obj" in args[1]


# SnapshotsClient

class TestSnapshotsClient:
    def test_create_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "snapshot_id": "snap_1", "name": "s", "template_id": "t",
            "vcpu": 1, "memory_mib": 512, "disk_mib": 10240,
            "network_policy": None, "created_at": "",
        }
        client = SnapshotsClient(t)
        client.create("sbx_1", name="my-snap")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/sandbox/sbx_1/snapshot/create"
        assert kwargs["json"]["name"] == "my-snap"

    def test_resume_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "sbx_new", "template_id": "t", "vcpu": 1, "memory_mib": 512,
            "disk_mib": 10240, "state": "starting", "auto_pause": False, "created_at": "",
        }
        client = SnapshotsClient(t)
        client.resume(snapshot_name="my-snap")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/snapshot/resume"
        assert kwargs["json"]["snapshot_name"] == "my-snap"

    def test_delete_url(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = SnapshotsClient(t)
        client.delete("snap_1")

        args, kwargs = t.request.call_args
        assert args[0] == "DELETE"
        assert args[1] == "/v1/snapshot/snap_1"

    def test_delete_accepts_snapshot_object(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = SnapshotsClient(t)
        snap = Snapshot(snapshot_id="snap_obj", name="n")
        client.delete(snap)

        args, _ = t.request.call_args
        assert "snap_obj" in args[1]


# TemplatesClient

class TestTemplatesClient:
    def test_create_url_and_payload(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "tpl_1", "name": "my-tpl", "digest": "sha256:abc",
            "image_config": None, "is_system": False, "created_at": "",
        }
        client = TemplatesClient(t)
        result = client.create(name="my-tpl", uri="docker.io/library/python:3.12")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/template"
        assert kwargs["json"]["name"] == "my-tpl"
        assert kwargs["json"]["uri"] == "docker.io/library/python:3.12"
        assert result.name == "my-tpl"

    def test_rename_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "tpl_1", "name": "new-name", "digest": "",
            "image_config": None, "is_system": False, "created_at": "",
        }
        client = TemplatesClient(t)
        result = client.rename("tpl_1", name="new-name")

        args, kwargs = t.request_json.call_args
        assert args[0] == "PATCH"
        assert args[1] == "/v1/template/tpl_1"
        assert kwargs["json"] == {"name": "new-name"}
        assert result.name == "new-name"

    def test_delete_url(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = TemplatesClient(t)
        client.delete("tpl_1")

        args, kwargs = t.request.call_args
        assert args[0] == "DELETE"
        assert args[1] == "/v1/template/tpl_1"
        assert kwargs["expected_status"] == 204


# FilesystemClient

class TestFilesystemClient:
    def test_ls_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"items": []}
        client = FilesystemClient(t)
        client.ls("sbx_1", path="/workspace")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/sandbox/sbx_1/filesystem/ls"
        assert kwargs["json"]["path"] == "/workspace"

    def test_mkdir_url(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = FilesystemClient(t)
        client.mkdir("sbx_1", path="/workspace/src", recursive=True)

        args, kwargs = t.request.call_args
        assert args[0] == "POST"
        assert "/filesystem/mkdir" in args[1]
        assert kwargs["json"]["recursive"] is True

    def test_exists_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"exists": True}
        client = FilesystemClient(t)
        result = client.exists("sbx_1", path="/workspace/main.py")

        assert result is True
        args, kwargs = t.request_json.call_args
        assert "/filesystem/exists" in args[1]

    def test_glob_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"items": ["/a.ts", "/b.ts"]}
        client = FilesystemClient(t)
        result = client.glob("sbx_1", path="/workspace", pattern="*.ts")

        assert result == ["/a.ts", "/b.ts"]

    def test_edit_file_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"diff": "...", "replacements": 1}
        client = FilesystemClient(t)
        edits = [FileEdit(find="old", replace="new")]
        client.edit_file("sbx_1", path="/a.py", edits=edits)

        args, kwargs = t.request_json.call_args
        assert "/filesystem/edit-file" in args[1]
        assert kwargs["json"]["edits"] == [{"find": "old", "replace": "new"}]


# Multipart parser

class TestParseMultipartResponse:
    def test_valid_multipart(self):
        boundary = "boundary123"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="/workspace/a.txt"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
            f"content a\r\n"
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="/workspace/b.txt"\r\n'
            f"Content-Type: application/octet-stream\r\n\r\n"
            f"content b\r\n"
            f"--{boundary}--\r\n"
        ).encode()
        ct = f"multipart/form-data; boundary={boundary}"
        result = _parse_multipart_response(ct, body)
        assert result["/workspace/a.txt"] == b"content a"
        assert result["/workspace/b.txt"] == b"content b"

    def test_non_multipart_raises(self):
        with pytest.raises(ValueError, match="Expected multipart"):
            _parse_multipart_response("application/json", b'{"error": "bad"}')


# GitClient

class TestGitClient:
    def test_clone_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"output": "cloned", "exit_code": 0}
        client = GitClient(t)
        client.clone("sbx_1", url="https://github.com/test/repo.git", path="/workspace/repo")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert args[1] == "/v1/sandbox/sbx_1/git/clone"
        assert kwargs["json"]["url"] == "https://github.com/test/repo.git"

    def test_status_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"output": "", "exit_code": 0}
        client = GitClient(t)
        client.status("sbx_1", path="/workspace/repo")

        args, kwargs = t.request_json.call_args
        assert "/git/status" in args[1]


# ProcessClient

class TestProcessClient:
    def test_execute_url(self):
        t = _mock_transport()
        t.request_json.return_value = {"exit_code": 0, "result": "hello"}
        client = ProcessClient(t)
        result = client.execute("sbx_1", command="echo hello")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert "/process/execute" in args[1]
        assert kwargs["json"]["command"] == "echo hello"
        assert result.exit_code == 0
        assert result.result == "hello"


# SshClient

class TestSshClient:
    def test_create_access_url(self):
        t = _mock_transport()
        t.request_json.return_value = {
            "id": "ssh_1", "password": "pw", "ssh_command": "ssh u@h",
            "sandbox_id": "sbx_1",
        }
        client = SshClient(t)
        result = client.create_access("sbx_1")

        args, kwargs = t.request_json.call_args
        assert args[0] == "POST"
        assert "/ssh/access" in args[1]
        assert result.id == "ssh_1"

    def test_delete_access_url(self):
        t = _mock_transport()
        t.request.return_value = MagicMock(status_code=204)
        client = SshClient(t)
        client.delete_access("sbx_1")

        args, kwargs = t.request.call_args
        assert args[0] == "DELETE"
        assert "/ssh/access" in args[1]
