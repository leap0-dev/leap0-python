"""Tests for Transport: auth, headers, check_response, URL handling."""
from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest

from leap0._sync._transport import Transport
from leap0.models.errors import (
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
        headers = transport.headers()
        assert headers["authorization"] == "Bearer test-key"
        assert headers["Leap0-Source"] == "sdk-python"
        assert headers["Leap0-SDK-Version"]
        assert headers["User-Agent"].startswith("leap0-python/")

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


class TestTimeoutHandling:
    def test_request_uses_zero_timeout(self, transport):
        transport._client = MagicMock()
        transport._client.request.return_value = MagicMock(spec=httpx.Response, status_code=200)

        transport.request("GET", "/test", timeout=0)

        assert transport._client.request.call_args.kwargs["timeout"] == 0

    def test_request_uses_zero_override(self, transport):
        transport._client = MagicMock()
        transport._client.request.return_value = MagicMock(spec=httpx.Response, status_code=200)

        with transport.override_timeout(0):
            transport.request("GET", "/test")

        assert transport._client.request.call_args.kwargs["timeout"] == 0

    def test_timeout_override_is_instance_scoped(self):
        first = Transport(api_key="k1", base_url="https://api.example.com")
        second = Transport(api_key="k2", base_url="https://api.example.com")
        first._client = MagicMock()
        second._client = MagicMock()
        first._client.request.return_value = MagicMock(spec=httpx.Response, status_code=200)
        second._client.request.return_value = MagicMock(spec=httpx.Response, status_code=200)

        with first.override_timeout(1.5):
            first.request("GET", "/first")
            second.request("GET", "/second")

        assert first._client.request.call_args.kwargs["timeout"] == 1.5
        assert second._client.request.call_args.kwargs["timeout"] == second.timeout
