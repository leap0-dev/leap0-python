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
        with pytest.raises(AttributeError, match=r"sandbox\.filesystem"):
            _ = client.filesystem
        client.close()

    def test_context_manager(self):
        with Leap0Client(api_key="test-key") as client:
            assert client.sandboxes is not None

    def test_otel_enabled_deprecation_shim(self):
        with pytest.warns(DeprecationWarning, match="sdk_otel_enabled"):
            client = Leap0Client(api_key="test-key", otel_enabled=False)

        client.close()

    def test_sdk_otel_enabled_wins_over_otel_enabled(self, monkeypatch):
        calls: list[bool] = []

        def fake_init_otel(self):
            calls.append(True)

        monkeypatch.setattr(Leap0Client, "_init_otel", fake_init_otel)

        with pytest.warns(DeprecationWarning, match="sdk_otel_enabled"):
            client = Leap0Client(api_key="test-key", otel_enabled=True, sdk_otel_enabled=False)

        client.close()
        assert calls == []
