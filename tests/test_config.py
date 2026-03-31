"""Tests for Leap0Config and Leap0Client initialization."""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from leap0.config import Leap0Config
from leap0.client import Leap0Client


class TestLeap0Config:
    def test_explicit_api_key(self):
        cfg = Leap0Config(api_key="my-key")
        assert cfg.api_key == "my-key"

    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "env-key"}):
            cfg = Leap0Config()
            assert cfg.api_key == "env-key"

    def test_raises_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LEAP0_API_KEY", None)
            with pytest.raises(ValueError, match="api_key is required"):
                Leap0Config()

    def test_explicit_key_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "env-key"}):
            cfg = Leap0Config(api_key="explicit-key")
            assert cfg.api_key == "explicit-key"

    def test_default_values(self):
        cfg = Leap0Config(api_key="key")
        assert cfg.base_url == "https://api.leap0.dev"
        assert cfg.sandbox_domain == "sandbox.leap0.dev"
        assert cfg.timeout == 300.0
        assert cfg.auth_header == "authorization"
        assert cfg.bearer is True

    def test_base_url_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "key", "LEAP0_BASE_URL": "https://api.custom.dev"}):
            cfg = Leap0Config()
            assert cfg.base_url == "https://api.custom.dev"

    def test_sandbox_domain_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "key", "LEAP0_SANDBOX_DOMAIN": "sandbox.custom.dev"}):
            cfg = Leap0Config()
            assert cfg.sandbox_domain == "sandbox.custom.dev"

    def test_explicit_base_url_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_BASE_URL": "https://api.env.dev"}):
            cfg = Leap0Config(api_key="key", base_url="https://api.explicit.dev")
            assert cfg.base_url == "https://api.explicit.dev"

    def test_explicit_sandbox_domain_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_SANDBOX_DOMAIN": "sandbox.env.dev"}):
            cfg = Leap0Config(api_key="key", sandbox_domain="sandbox.explicit.dev")
            assert cfg.sandbox_domain == "sandbox.explicit.dev"


class TestLeap0Client:
    def test_raises_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LEAP0_API_KEY", None)
            with pytest.raises(ValueError, match="api_key is required"):
                Leap0Client()

    def test_creates_with_explicit_key(self):
        client = Leap0Client(api_key="test-key")
        assert client.sandboxes is not None
        assert client.templates is not None
        assert client.filesystem is not None
        assert client.git is not None
        assert client.process is not None
        assert client.pty is not None
        assert client.lsp is not None
        assert client.ssh is not None
        assert client.code_interpreter is not None
        assert client.desktop is not None
        assert client.snapshots is not None
        client.close()

    def test_context_manager(self):
        with Leap0Client(api_key="test-key") as client:
            assert client.sandboxes is not None

    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "env-key"}):
            client = Leap0Client()
            client.close()

    def test_base_url_from_env(self):
        with patch.dict(os.environ, {"LEAP0_BASE_URL": "https://api.custom.dev"}):
            client = Leap0Client(api_key="test-key")
            assert client._transport.base_url == "https://api.custom.dev"
            client.close()

    def test_sandbox_domain_from_env(self):
        with patch.dict(os.environ, {"LEAP0_SANDBOX_DOMAIN": "sandbox.custom.dev"}):
            client = Leap0Client(api_key="test-key")
            assert client.sandboxes._sandbox_domain == "sandbox.custom.dev"
            assert client.desktop._sandbox_domain == "sandbox.custom.dev"
            assert client.code_interpreter._sandbox_domain == "sandbox.custom.dev"
            client.close()

    def test_explicit_base_url_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_BASE_URL": "https://api.env.dev"}):
            client = Leap0Client(api_key="test-key", base_url="https://api.explicit.dev")
            assert client._transport.base_url == "https://api.explicit.dev"
            client.close()

    def test_explicit_sandbox_domain_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_SANDBOX_DOMAIN": "sandbox.env.dev"}):
            client = Leap0Client(api_key="test-key", sandbox_domain="sandbox.explicit.dev")
            assert client.sandboxes._sandbox_domain == "sandbox.explicit.dev"
            client.close()
