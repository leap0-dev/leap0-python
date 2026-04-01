from __future__ import annotations

import httpx
import pytest

from leap0.models.errors import Leap0Error, Leap0NotFoundError, Leap0TimeoutError
from leap0._utils.errors import intercept_errors


class TestInterceptErrors:
    def test_prefix_prepended(self):
        @intercept_errors("Failed to delete file: ")
        def failing():
            raise Leap0NotFoundError("Request failed", 404, body='{"message":"not found"}')

        with pytest.raises(Leap0NotFoundError) as exc_info:
            failing()
        assert exc_info.value.message.startswith("Failed to delete file: ")

    def test_sdk_error_is_recreated_not_mutated(self):
        original = Leap0NotFoundError("Request failed", 404, body='{"message":"not found"}')

        @intercept_errors("Failed to delete file: ")
        def failing():
            raise original

        with pytest.raises(Leap0NotFoundError) as exc_info:
            failing()
        assert exc_info.value is not original
        assert original.message == "Request failed"

    def test_httpx_timeout(self):
        @intercept_errors("Failed to read file: ")
        def failing():
            raise httpx.ReadTimeout("timed out")

        with pytest.raises(Leap0TimeoutError):
            failing()

    def test_httpx_connect_error(self):
        @intercept_errors("Failed to create sandbox: ")
        def failing():
            raise httpx.ConnectError("connection refused")

        with pytest.raises(Leap0Error) as exc_info:
            failing()
        assert type(exc_info.value) is Leap0Error

    def test_generic_exception(self):
        @intercept_errors("Failed: ")
        def failing():
            raise RuntimeError("broke")

        with pytest.raises(Leap0Error):
            failing()

    def test_no_double_prefix(self):
        @intercept_errors("Failed to write file: ")
        def failing():
            raise Leap0Error("Failed to write file: already prefixed", 400)

        with pytest.raises(Leap0Error) as exc_info:
            failing()
        assert not exc_info.value.message.startswith("Failed to write file: Failed to write file: ")

    def test_closed_client_runtime_error(self):
        @intercept_errors("Failed to list directory: ")
        def failing():
            raise RuntimeError("Cannot send a request, as the client has been closed.")

        with pytest.raises(Leap0Error) as exc_info:
            failing()
        assert "client is closed" in exc_info.value.message

    def test_success_passes_through(self):
        @intercept_errors("Nope: ")
        def ok():
            return 42

        assert ok() == 42
