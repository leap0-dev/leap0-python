from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from leap0.models.config import Leap0Config
from leap0._sync.client import Leap0Client


class TestLeap0Config:
    def test_explicit_api_key(self):
        assert Leap0Config(api_key="my-key").api_key == "my-key"

    def test_api_key_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "env-key"}):
            assert Leap0Config().api_key == "env-key"

    def test_raises_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LEAP0_API_KEY", None)
            with pytest.raises(ValueError, match="api_key is required"):
                Leap0Config()

    def test_explicit_key_overrides_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "env-key"}):
            assert Leap0Config(api_key="explicit-key").api_key == "explicit-key"

    def test_default_values(self):
        cfg = Leap0Config(api_key="key")
        assert cfg.base_url == "https://api.leap0.dev"
        assert cfg.sandbox_domain == "sandbox.leap0.dev"
        assert cfg.timeout == 300.0

    def test_base_url_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "key", "LEAP0_BASE_URL": "https://api.custom.dev"}):
            assert Leap0Config().base_url == "https://api.custom.dev"

    def test_sandbox_domain_from_env(self):
        with patch.dict(os.environ, {"LEAP0_API_KEY": "key", "LEAP0_SANDBOX_DOMAIN": "sandbox.custom.dev"}):
            assert Leap0Config().sandbox_domain == "sandbox.custom.dev"


class TestLeap0Client:
    def test_raises_when_no_key(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("LEAP0_API_KEY", None)
            with pytest.raises(ValueError):
                Leap0Client()

    def test_creates_with_key(self):
        client = Leap0Client(api_key="test-key")
        assert client.sandboxes is not None
        assert client.filesystem is not None
        client.close()

    def test_context_manager(self):
        with Leap0Client(api_key="test-key") as client:
            assert client.sandboxes is not None
