from __future__ import annotations

from leap0.models.config import Leap0Config


def test_otel_enabled_defaults_from_standard_otel_env(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    config = Leap0Config()

    assert config.otel_enabled is True


def test_otel_enabled_can_be_disabled_explicitly(monkeypatch):
    monkeypatch.setenv("LEAP0_API_KEY", "test-key")
    monkeypatch.setenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")

    config = Leap0Config(otel_enabled=False)

    assert config.otel_enabled is False
