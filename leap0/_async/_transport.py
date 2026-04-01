from __future__ import annotations

from contextlib import asynccontextmanager
from contextvars import ContextVar
from typing import BinaryIO

import httpx

from .._internal.types import BinaryFiles, JsonObject
from .._internal.version import SDK_VERSION
from .._utils.otel import with_instrumentation
from ..models.config import DEFAULT_CLIENT_TIMEOUT
from ..models.errors import raise_api_error


class AsyncTransport:
    """HTTP transport for asynchronous SDK requests.
    
    Attributes:
        api_key: Public attribute exposed by this object.
        base_url: Public attribute exposed by this object.
        timeout: Public attribute exposed by this object.
        auth_header: Public attribute exposed by this object.
        bearer: Public attribute exposed by this object.
    """
    _timeout_override: ContextVar[float | None] = ContextVar("leap0_async_timeout_override", default=None)

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = DEFAULT_CLIENT_TIMEOUT,
        auth_header: str = "authorization",
        bearer: bool = True,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.auth_header = auth_header
        self.bearer = bearer
        self._client = httpx.AsyncClient(timeout=timeout)

    @property
    def auth_value(self) -> str:
        """Return the formatted authorization header value.
        
        Returns:
            object: Result returned by this operation.
        """
        if self.bearer and not self.api_key.lower().startswith("bearer "):
            return f"Bearer {self.api_key}"
        return self.api_key

    async def close(self) -> None:
        """Close the client and release resources."""
        await self._client.aclose()

    @asynccontextmanager
    async def override_timeout(self, timeout: float | None):
        """Temporarily override the transport timeout for nested calls.
        
        Args:
            timeout: Operation timeout in seconds.
        
        Yields:
            object: Items yielded by this operation.
        """
        if timeout is None:
            yield
            return
        token = self._timeout_override.set(timeout)
        try:
            yield
        finally:
            self._timeout_override.reset(token)

    def headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Build request headers for the current transport.
        
        Args:
            extra: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        headers = {
            self.auth_header: self.auth_value,
            "Leap0-Source": "sdk-python-async",
            "Leap0-SDK-Version": SDK_VERSION,
            "User-Agent": f"leap0-python-async/{SDK_VERSION}",
        }
        if extra:
            headers.update(extra)
        return headers

    def _expected(self, expected_status: int | tuple[int, ...]) -> tuple[int, ...]:
        return (expected_status,) if isinstance(expected_status, int) else expected_status

    def _target_url(self, target: str) -> str:
        if target.startswith("https://") or target.startswith("http://"):
            return target
        return f"{self.base_url}{target}"

    def _check_response(
        self,
        response: httpx.Response,
        method: str,
        target: str,
        expected_status: int | tuple[int, ...],
    ) -> httpx.Response:
        expected = self._expected(expected_status)
        if response.status_code not in expected:
            raise_api_error(
                response.status_code,
                f"Request failed: {method} {target}",
                body=response.text,
                headers=dict(response.headers),
            )
        return response

    @with_instrumentation("async_transport.target_request")
    async def _request(
        self,
        method: str,
        target: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        content: bytes | str | BinaryIO | None = None,
        files: BinaryFiles | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> httpx.Response:
        response = await self._client.request(
            method,
            self._target_url(target),
            params=params,
            json=json,
            content=content,
            files=files,
            headers=self.headers(headers),
            timeout=timeout or self._timeout_override.get() or self.timeout,
        )
        return self._check_response(response, method, target, expected_status)

    @with_instrumentation("async_transport.stream")
    async def _stream(
        self,
        method: str,
        target: str,
        *,
        json: JsonObject | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        effective = timeout if timeout is not None else (self._timeout_override.get() or self.timeout)
        timeout_dict = {"connect": effective, "read": effective, "write": effective, "pool": effective}
        request = self._client.build_request(
            method,
            self._target_url(target),
            json=json,
            headers=self.headers(),
            extensions={"timeout": timeout_dict},
        )
        response = await self._client.send(request, stream=True)
        if response.status_code >= 400:
            body = (await response.aread()).decode("utf-8", errors="replace")
            hdrs = dict(response.headers)
            await response.aclose()
            raise_api_error(response.status_code, f"Request failed: {method} {target}", body=body, headers=hdrs)
        return response

    @with_instrumentation("async_transport.request")
    async def request(
        self,
        method: str,
        path: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        content: bytes | str | BinaryIO | None = None,
        files: BinaryFiles | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an HTTP request to a control-plane path.
        
        Args:
            method: Parameter for this operation.
            path: Path used by this operation.
            params: Parameter for this operation.
            json: Parameter for this operation.
            content: Parameter for this operation.
            files: Parameter for this operation.
            headers: Parameter for this operation.
            expected_status: Parameter for this operation.
            timeout: Operation timeout in seconds.
        
        Returns:
            object: Result returned by this operation.
        """
        return await self._request(
            method,
            f"{self.base_url}{path}",
            params=params,
            json=json,
            content=content,
            files=files,
            headers=headers,
            expected_status=expected_status,
            timeout=timeout,
        )

    @with_instrumentation("async_transport.request_json")
    async def request_json(
        self,
        method: str,
        path: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        content: bytes | str | BinaryIO | None = None,
        files: BinaryFiles | None = None,
        headers: dict[str, str] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> JsonObject:
        """Send an HTTP request and parse the JSON response.
        
        Args:
            method: Parameter for this operation.
            path: Path used by this operation.
            params: Parameter for this operation.
            json: Parameter for this operation.
            content: Parameter for this operation.
            files: Parameter for this operation.
            headers: Parameter for this operation.
            expected_status: Parameter for this operation.
            timeout: Operation timeout in seconds.
        
        Returns:
            object: Result returned by this operation.
        """
        response = await self.request(
            method,
            path,
            params=params,
            json=json,
            content=content,
            files=files,
            headers=headers,
            expected_status=expected_status,
            timeout=timeout,
        )
        return response.json()

    @with_instrumentation("async_transport.request_target")
    async def request_target(
        self,
        method: str,
        target: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Send an HTTP request to a fully qualified target URL.
        
        Args:
            method: Parameter for this operation.
            target: Parameter for this operation.
            params: Parameter for this operation.
            json: Parameter for this operation.
            expected_status: Parameter for this operation.
            timeout: Operation timeout in seconds.
        
        Returns:
            object: Result returned by this operation.
        """
        return await self._request(
            method,
            target,
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=timeout,
        )

    @with_instrumentation("async_transport.request_target_json")
    async def request_target_json(
        self,
        method: str,
        target: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        timeout: float | None = None,
    ) -> JsonObject:
        """Send an HTTP request to a target URL and parse JSON.
        
        Args:
            method: Parameter for this operation.
            target: Parameter for this operation.
            params: Parameter for this operation.
            json: Parameter for this operation.
            expected_status: Parameter for this operation.
            timeout: Operation timeout in seconds.
        
        Returns:
            object: Result returned by this operation.
        """
        response = await self.request_target(
            method,
            target,
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=timeout,
        )
        return response.json()

    async def stream(
        self,
        method: str,
        target: str,
        *,
        json: JsonObject | None = None,
        timeout: float | None = None,
    ) -> httpx.Response:
        """Open a streaming HTTP response.
        
        Args:
            method: Parameter for this operation.
            target: Parameter for this operation.
            json: Parameter for this operation.
            timeout: Operation timeout in seconds.
        
        Returns:
            object: Result returned by this operation.
        """
        return await self._stream(method, target, json=json, timeout=timeout)
