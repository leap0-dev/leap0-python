"""Tests for Transport: auth, headers, check_response, URL handling."""
from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from leap0._transport import Transport
from leap0.common.errors import (
    Leap0ConflictError, Leap0Error, Leap0NotFoundError, Leap0PermissionError, Leap0RateLimitError,
)


class TestAuthValue:
    def test_bearer_prefix_added(self, transport):
        assert transport.auth_value == "Bearer test-key"

    def test_bearer_not_doubled(self):
        assert Transport(api_key="Bearer already", base_url="https://x.com").auth_value == "Bearer already"

    def test_bearer_disabled(self):
        assert Transport(api_key="raw", base_url="https://x.com", bearer=False).auth_value == "raw"


class TestHeaders:
    def test_default(self, transport):
        assert transport.headers() == {"authorization": "Bearer test-key"}

    def test_custom_auth_header(self):
        t = Transport(api_key="key", base_url="https://x.com", auth_header="leap0-authorization")
        assert t.headers()["leap0-authorization"] == "Bearer key"

    def test_extra_merged(self, transport):
        h = transport.headers({"Content-Type": "application/json"})
        assert h["Content-Type"] == "application/json"


class TestCheckResponse:
    def test_pass_on_expected(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=200)
        assert transport._check_response(resp, "GET", "/test", 200) is resp

    def test_404(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=404, text='{"message":"not found"}', headers={})
        with pytest.raises(Leap0NotFoundError):
            transport._check_response(resp, "GET", "/test", 200)

    def test_403(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=403, text='{"message":"denied"}', headers={})
        with pytest.raises(Leap0PermissionError):
            transport._check_response(resp, "POST", "/test", 200)

    def test_409(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=409, text="{}", headers={})
        with pytest.raises(Leap0ConflictError):
            transport._check_response(resp, "POST", "/test", 200)

    def test_429(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=429, text="", headers={"Retry-After": "30"})
        with pytest.raises(Leap0RateLimitError) as exc_info:
            transport._check_response(resp, "GET", "/test", 200)
        assert exc_info.value.headers["Retry-After"] == "30"

    def test_500_base_error(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=500, text="err", headers={})
        with pytest.raises(Leap0Error) as exc_info:
            transport._check_response(resp, "POST", "/x", 200)
        assert type(exc_info.value) is Leap0Error

    def test_json_body_parsed(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=400,
                         text='{"message":"path cannot be empty"}', headers={})
        with pytest.raises(Leap0Error) as exc_info:
            transport._check_response(resp, "POST", "/test", 200)
        assert exc_info.value.error_message == "path cannot be empty"

    def test_non_json_body(self, transport):
        resp = MagicMock(spec=httpx.Response, status_code=500, text="plain", headers={})
        with pytest.raises(Leap0Error) as exc_info:
            transport._check_response(resp, "POST", "/test", 200)
        assert exc_info.value.error_message is None


class TestTargetUrl:
    def test_absolute(self, transport):
        assert transport._target_url("https://other.com/api") == "https://other.com/api"

    def test_relative(self, transport):
        assert transport._target_url("/v1/sandbox") == "https://api.example.com/v1/sandbox"


class TestBaseUrlNormalization:
    def test_trailing_slash_stripped(self):
        assert Transport(api_key="k", base_url="https://api.example.com/").base_url == "https://api.example.com"
