"""Tests for Transport: auth, headers, check_response."""
from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from leap0._transport import Transport
from leap0.exceptions import Leap0APIError


@pytest.fixture
def transport():
    return Transport(api_key="test-key", base_url="https://api.example.com")


class TestAuthValue:
    def test_bearer_prefix_added(self, transport: Transport):
        assert transport.auth_value == "Bearer test-key"

    def test_bearer_not_doubled(self):
        t = Transport(api_key="Bearer already", base_url="https://api.example.com")
        assert t.auth_value == "Bearer already"

    def test_bearer_case_insensitive(self):
        t = Transport(api_key="bearer test", base_url="https://api.example.com")
        assert t.auth_value == "bearer test"

    def test_bearer_disabled(self):
        t = Transport(api_key="raw-key", base_url="https://api.example.com", bearer=False)
        assert t.auth_value == "raw-key"


class TestHeaders:
    def test_default_headers(self, transport: Transport):
        h = transport.headers()
        assert h == {"authorization": "Bearer test-key"}

    def test_custom_auth_header(self):
        t = Transport(api_key="key", base_url="https://api.example.com", auth_header="leap0-authorization")
        h = t.headers()
        assert "leap0-authorization" in h
        assert h["leap0-authorization"] == "Bearer key"

    def test_extra_headers_merged(self, transport: Transport):
        h = transport.headers({"Content-Type": "application/json"})
        assert h["authorization"] == "Bearer test-key"
        assert h["Content-Type"] == "application/json"

    def test_extra_headers_override(self, transport: Transport):
        h = transport.headers({"authorization": "override"})
        assert h["authorization"] == "override"


class TestCheckResponse:
    def test_pass_on_expected(self, transport: Transport):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 200
        result = transport._check_response(resp, "GET", "/test", 200)
        assert result is resp

    def test_pass_on_multiple_expected(self, transport: Transport):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 201
        result = transport._check_response(resp, "POST", "/test", (200, 201))
        assert result is resp

    def test_raise_on_unexpected(self, transport: Transport):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 404
        resp.text = "not found"
        with pytest.raises(Leap0APIError) as exc_info:
            transport._check_response(resp, "GET", "/test", 200)
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value)

    def test_raise_on_500(self, transport: Transport):
        resp = MagicMock(spec=httpx.Response)
        resp.status_code = 500
        resp.text = "internal error"
        with pytest.raises(Leap0APIError) as exc_info:
            transport._check_response(resp, "POST", "/create", 201)
        assert exc_info.value.status_code == 500


class TestTargetUrl:
    def test_absolute_url_passthrough(self, transport: Transport):
        assert transport._target_url("https://sandbox.example.com/api") == "https://sandbox.example.com/api"

    def test_relative_path_prepends_base(self, transport: Transport):
        assert transport._target_url("/v1/sandbox") == "https://api.example.com/v1/sandbox"

    def test_http_url_passthrough(self, transport: Transport):
        assert transport._target_url("http://local:8080/api") == "http://local:8080/api"


class TestBaseUrlNormalization:
    def test_trailing_slash_stripped(self):
        t = Transport(api_key="key", base_url="https://api.example.com/")
        assert t.base_url == "https://api.example.com"

    def test_no_trailing_slash(self):
        t = Transport(api_key="key", base_url="https://api.example.com")
        assert t.base_url == "https://api.example.com"
