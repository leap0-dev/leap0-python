from __future__ import annotations

import pytest

from leap0.models.config import Leap0Config


def test_sdk_otel_enabled_defaults_from_standard_otel_env(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    config = Leap0Config()

    assert config.sdk_otel_enabled is True


def test_sdk_otel_enabled_can_be_disabled_explicitly(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    config = Leap0Config(sdk_otel_enabled=False)

    assert config.sdk_otel_enabled is False


def test_explicit_sdk_flag_precedence(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("LEAP0_SDK_OTEL_ENABLED", "false")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    config = Leap0Config()

    assert config.sdk_otel_enabled is False


def test_sdk_otel_enabled_accepts_case_insensitive_values(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("LEAP0_SDK_OTEL_ENABLED", "TrUe")

    assert Leap0Config().sdk_otel_enabled is True

    monkeypatch.setenv("LEAP0_SDK_OTEL_ENABLED", "FaLsE")
    assert Leap0Config().sdk_otel_enabled is False


def test_sdk_otel_enabled_rejects_invalid_string(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("LEAP0_SDK_OTEL_ENABLED", "maybe")

    with pytest.raises(ValueError, match="invalid LEAP0_SDK_OTEL_ENABLED value: maybe"):
        Leap0Config()


def test_legacy_otel_env_no_longer_enables_sdk(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("LEAP0_OTEL_ENABLED", "true")
    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)

    config = Leap0Config()

    assert config.sdk_otel_enabled is False
