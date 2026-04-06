from __future__ import annotations

import asyncio
import time
from collections.abc import AsyncIterator
from typing import cast

import httpx
from pydantic import ValidationError

from .._internal.types import JsonObject
from ..models.desktop import (
    DesktopClickParams,
    DesktopDisplayInfo,
    DesktopDisplayInfoDict,
    DesktopHealth,
    DesktopHealthDict,
    DesktopOkResponse,
    DesktopPointerPosition,
    DesktopPointerPositionDict,
    DesktopProcessErrors,
    DesktopProcessErrorsDict,
    DesktopProcessLogs,
    DesktopProcessLogsDict,
    DesktopProcessRestart,
    DesktopProcessRestartDict,
    DesktopProcessStatus,
    DesktopProcessStatusDict,
    DesktopProcessStatusList,
    DesktopProcessStatusListDict,
    DesktopRecordingStatus,
    DesktopRecordingStatusDict,
    DesktopRecordingSummary,
    DesktopRecordingSummaryDict,
    DesktopResizeScreenParams,
    DesktopScreenshotParams,
    DesktopScreenshotRegionParams,
    DesktopStatusStreamErrorEvent,
    DesktopWindow,
    DesktopWindowsDict,
)
from ..models.sandbox import SandboxRef, sandbox_id_of
from ..models.errors import Leap0Error, Leap0TimeoutError
from .._utils.errors import intercept_errors
from .._utils.stream import aiter_sse_events
from .._utils.url import sandbox_base_url
from ._transport import AsyncTransport


class AsyncDesktopClient:
    """Control a sandbox desktop through asynchronous APIs.
    
    Attributes:
        None.
    """
    def __init__(self, transport: AsyncTransport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    async def _request(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> httpx.Response:
        return await self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    async def _request_json(
        self,
        method: str,
        sandbox: SandboxRef,
        path: str,
        *,
        params: JsonObject | None = None,
        json: JsonObject | None = None,
        expected_status: int | tuple[int, ...] = 200,
        http_timeout: float | None = None,
    ) -> JsonObject:
        return await self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    def desktop_url(self, sandbox: SandboxRef) -> str:
        """Build the browser URL for the desktop viewer.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/"

    @intercept_errors("Failed to get display info: ")
    async def display_info(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get display information for the desktop.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopDisplayInfoDict, await self._request_json("GET", sandbox, "/api/display"))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to get screen info: ")
    async def screen(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get the current desktop screen geometry.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopDisplayInfoDict, await self._request_json("GET", sandbox, "/api/display/screen"))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to resize screen: ")
    async def resize_screen(self, sandbox: SandboxRef, *, width: int, height: int, http_timeout: float | None = None) -> DesktopDisplayInfo:
        """
                            Resize the virtual display (width: 320-7680, height: 320-4320).
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload = DesktopResizeScreenParams(width=width, height=height).model_dump()
        data = cast(DesktopDisplayInfoDict, await self._request_json("POST", sandbox, "/api/display/screen", json=payload, http_timeout=http_timeout))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to list windows: ")
    async def windows(self, sandbox: SandboxRef) -> list[DesktopWindow]:
        """List open desktop windows.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopWindowsDict, await self._request_json("GET", sandbox, "/api/display/windows"))
        return [DesktopWindow.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to take screenshot: ")
    async def screenshot(
        self,
        sandbox: SandboxRef,
        *,
        image_format: str | None = None,
        quality: int | None = None,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
        http_timeout: float | None = None,
    ) -> bytes:
        """Take a screenshot and return the image as bytes.
                
                        Args:
                            sandbox: Sandbox ID or object.
                            image_format: ``"png"``, ``"jpg"``, or ``"jpeg"`` (default ``"png"``).
                            quality: JPEG quality (1-100).
                            x: Left edge of capture region.
                            y: Top edge of capture region.
                            width: Region width in pixels.
                            height: Region height in pixels.
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        params = DesktopScreenshotParams(
            format=image_format,
            quality=quality,
            x=x,
            y=y,
            width=width,
            height=height,
        ).model_dump(exclude_none=True)
        response = await self._request("GET", sandbox, "/api/screenshot", params=params or None, http_timeout=http_timeout)
        return response.content

    @intercept_errors("Failed to take screenshot: ")
    async def screenshot_region(
        self,
        sandbox: SandboxRef,
        *,
        x: int,
        y: int,
        width: int,
        height: int,
        image_format: str | None = None,
        quality: int | None = None,
        http_timeout: float | None = None,
    ) -> bytes:
        """
                            Take a screenshot of a specific region and return the image as bytes.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload = DesktopScreenshotRegionParams(
            x=x,
            y=y,
            width=width,
            height=height,
            format=image_format,
            quality=quality,
        ).model_dump(exclude_none=True)
        response = await self._request("POST", sandbox, "/api/screenshot/region", json=payload, http_timeout=http_timeout)
        return response.content

    @intercept_errors("Failed to get pointer position: ")
    async def pointer_position(self, sandbox: SandboxRef) -> DesktopPointerPosition:
        """Get the current pointer position.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopPointerPositionDict, await self._request_json("GET", sandbox, "/api/input/position"))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to move pointer: ")
    async def move_pointer(self, sandbox: SandboxRef, *, x: int, y: int, http_timeout: float | None = None) -> DesktopPointerPosition:
        """
                            Move the mouse pointer to the given coordinates.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopPointerPositionDict, await self._request_json("POST", sandbox, "/api/input/move", json={"x": x, "y": y}, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to click: ")
    async def click(self, sandbox: SandboxRef, *, x: int | None = None, y: int | None = None, button: int | None = None, http_timeout: float | None = None) -> DesktopPointerPosition:
        """Click the mouse. Clicks at the current position if coordinates are omitted.
                
                        Args:
                            sandbox: Sandbox ID or object.
                            x: X coordinate.
                            y: Y coordinate.
                            button: 1=left, 2=middle, 3=right (default 1).
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload = DesktopClickParams(x=x, y=y, button=button).model_dump(exclude_none=True)
        data = cast(DesktopPointerPositionDict, await self._request_json("POST", sandbox, "/api/input/click", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to drag: ")
    async def drag(self, sandbox: SandboxRef, *, from_x: int, from_y: int, to_x: int, to_y: int, button: int | None = None, http_timeout: float | None = None) -> DesktopPointerPosition:
        """
                            Drag from one position to another.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"from_x": from_x, "from_y": from_y, "to_x": to_x, "to_y": to_y}
        if button is not None:
            payload["button"] = button
        data = cast(DesktopPointerPositionDict, await self._request_json("POST", sandbox, "/api/input/drag", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to scroll: ")
    async def scroll(self, sandbox: SandboxRef, *, direction: str, amount: int | None = None, http_timeout: float | None = None) -> DesktopPointerPosition:
        """Scroll the mouse wheel.
                
                        Args:
                            sandbox: Sandbox ID or object.
                            direction: ``"up"``, ``"down"``, ``"left"``, or ``"right"``.
                            amount: Number of scroll steps (1-100, default 1).
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {"direction": direction}
        if amount is not None:
            payload["amount"] = amount
        data = cast(DesktopPointerPositionDict, await self._request_json("POST", sandbox, "/api/input/scroll", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to type text: ")
    async def type_text(self, sandbox: SandboxRef, *, text: str, http_timeout: float | None = None) -> bool:
        """Type text through the desktop input service.
        
        Args:
            sandbox: Sandbox ID or object.
            text: Text to type.
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = await self._request_json("POST", sandbox, "/api/input/type", json={"text": text}, http_timeout=http_timeout)
        return DesktopOkResponse.model_validate(data).ok

    @intercept_errors("Failed to press key: ")
    async def press_key(self, sandbox: SandboxRef, *, key: str, http_timeout: float | None = None) -> bool:
        """
                            Press a single key by X11 keysym name (e.g. ``"Return"``, ``"Escape"``).
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = await self._request_json("POST", sandbox, "/api/input/press", json={"key": key}, http_timeout=http_timeout)
        return DesktopOkResponse.model_validate(data).ok

    @intercept_errors("Failed to press hotkey: ")
    async def hotkey(self, sandbox: SandboxRef, *, keys: list[str]) -> bool:
        """Send a multi-key hotkey combination.
        
        Args:
            sandbox: Sandbox ID or object.
            keys: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        data = await self._request_json("POST", sandbox, "/api/input/hotkey", json={"keys": keys})
        return DesktopOkResponse.model_validate(data).ok

    @intercept_errors("Failed to get recording status: ")
    async def recording_status(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopRecordingStatus:
        """
                            Get the current screen recording status.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, await self._request_json("GET", sandbox, "/api/recording", http_timeout=http_timeout))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to start recording: ")
    async def start_recording(self, sandbox: SandboxRef) -> DesktopRecordingStatus:
        """Start desktop recording.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, await self._request_json("POST", sandbox, "/api/recording/start", expected_status=201))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to stop recording: ")
    async def stop_recording(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopRecordingStatus:
        """
                            Stop the active screen recording.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, await self._request_json("POST", sandbox, "/api/recording/stop", http_timeout=http_timeout))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to list recordings: ")
    async def recordings(self, sandbox: SandboxRef) -> list[DesktopRecordingSummary]:
        """List saved desktop recordings.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        raw = await self._request_json("GET", sandbox, "/api/recordings")
        items = cast(list[DesktopRecordingSummaryDict], raw.get("items", []))
        return [DesktopRecordingSummary.from_dict(item) for item in items]

    @intercept_errors("Failed to get recording: ")
    async def get_recording(self, sandbox: SandboxRef, recording_id: str, http_timeout: float | None = None) -> DesktopRecordingSummary:
        """
                            Get details for a single recording.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingSummaryDict, await self._request_json("GET", sandbox, f"/api/recordings/{recording_id}", http_timeout=http_timeout))
        return DesktopRecordingSummary.from_dict(data)

    @intercept_errors("Failed to download recording: ")
    async def download_recording(self, sandbox: SandboxRef, recording_id: str) -> bytes:
        """Download a desktop recording as bytes.
        
        Args:
            sandbox: Sandbox ID or object.
            recording_id: Recording identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        response = await self._request("GET", sandbox, f"/api/recordings/{recording_id}/download")
        return response.content

    @intercept_errors("Failed to delete recording: ")
    async def delete_recording(self, sandbox: SandboxRef, recording_id: str, http_timeout: float | None = None) -> None:
        """
                    Delete a recording. Cannot delete an active recording.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
                
        """
        await self._request("DELETE", sandbox, f"/api/recordings/{recording_id}", expected_status=204, http_timeout=http_timeout)

    @intercept_errors("Failed to check desktop health: ")
    async def health(self, sandbox: SandboxRef) -> DesktopHealth:
        """Check service health.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopHealthDict, await self._request_json("GET", sandbox, "/api/healthz", expected_status=(200, 503)))
        return DesktopHealth.from_dict(data)

    @intercept_errors("Failed to get process status: ")
    async def process_status(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopProcessStatusList:
        """
                            Get the status of all desktop processes (xvfb, xfce4, x11vnc, novnc).
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessStatusListDict, await self._request_json("GET", sandbox, "/api/status", http_timeout=http_timeout))
        return DesktopProcessStatusList.from_dict(data)

    @intercept_errors("Failed to get process: ")
    async def get_process(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessStatus:
        """Get status for one desktop process.
        
        Args:
            sandbox: Sandbox ID or object.
            process_name: Desktop process name.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessStatusDict, await self._request_json("GET", sandbox, f"/api/process/{process_name}/status"))
        return DesktopProcessStatus.from_dict(data)

    @intercept_errors("Failed to restart process: ")
    async def restart_process(self, sandbox: SandboxRef, process_name: str, http_timeout: float | None = None) -> DesktopProcessRestart:
        """
                            Restart a desktop process.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessRestartDict, await self._request_json("POST", sandbox, f"/api/process/{process_name}/restart", http_timeout=http_timeout))
        return DesktopProcessRestart.from_dict(data)

    @intercept_errors("Failed to get process logs: ")
    async def process_logs(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessLogs:
        """Get logs for one desktop process.
        
        Args:
            sandbox: Sandbox ID or object.
            process_name: Desktop process name.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessLogsDict, await self._request_json("GET", sandbox, f"/api/process/{process_name}/logs"))
        return DesktopProcessLogs.from_dict(data)

    @intercept_errors("Failed to get process errors: ")
    async def process_errors(self, sandbox: SandboxRef, process_name: str, http_timeout: float | None = None) -> DesktopProcessErrors:
        """
                            Get stderr logs for a desktop process.
                
                            Args:
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessErrorsDict, await self._request_json("GET", sandbox, f"/api/process/{process_name}/errors", http_timeout=http_timeout))
        return DesktopProcessErrors.from_dict(data)

    @intercept_errors("Failed to stream status: ")
    async def status_stream(self, sandbox: SandboxRef, *, deadline: float | None = None, http_timeout: float | None = None) -> AsyncIterator[DesktopProcessStatusList]:
        """Subscribe to a live SSE stream of process status updates.
                
                        Args:
                            sandbox: Sandbox ID or object.
                            deadline: Absolute ``time.monotonic()`` deadline.  When set, a
                                :class:`Leap0TimeoutError` is raised once the deadline is
                                exceeded.  ``None`` means no deadline.
                            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Yields:
            object: Items yielded by this operation.
        """
        url = f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/api/status/stream"
        stream_timeout = http_timeout
        if deadline is not None:
            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                raise Leap0TimeoutError("Desktop status stream timed out")
            stream_timeout = remaining_time if stream_timeout is None else min(stream_timeout, remaining_time)
        response = await self._transport.stream("GET", url, timeout=stream_timeout)
        try:
            events = aiter_sse_events(response.aiter_lines())
            while True:
                if deadline is not None and time.monotonic() >= deadline:
                    raise Leap0TimeoutError("Desktop status stream timed out")
                try:
                    event = await events.__anext__()
                except StopAsyncIteration:
                    break
                if not isinstance(event, dict):
                    raise ValueError(
                        "Malformed desktop status stream event "
                        f"for sandbox={sandbox_id_of(sandbox)!r}, source='status_stream': {event!r}"
                    )
                try:
                    yield DesktopProcessStatusList.from_dict(cast(DesktopProcessStatusListDict, event))
                    continue
                except (TypeError, ValueError) as status_error:
                    try:
                        error_event = DesktopStatusStreamErrorEvent.model_validate(event)
                    except ValidationError:
                        raise status_error
                    raise Leap0Error("Desktop status stream error", body=error_event.detail) from status_error
        finally:
            await response.aclose()

    async def wait_until_ready(self, sandbox: SandboxRef, *, timeout: float = 60.0, http_timeout: float | None = None) -> None:
        """Block until all desktop processes are running.
        
                Connects to the SSE status stream and waits for the aggregate
                status to become ``"running"`` (all four desktop processes alive).
                Automatically retries the stream connection on transient errors
                using exponential back-off, bounded by *timeout* seconds total.
        
                Args:
                    sandbox: Sandbox ID or object.
                    timeout: Maximum seconds to wait (default 60).
        
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
                Raises:
                    Leap0TimeoutError: If the desktop does not become ready within
                        *timeout* seconds.
                
        """
        deadline = time.monotonic() + timeout
        delay = 0.5
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                async for status in self.status_stream(sandbox, deadline=deadline, http_timeout=http_timeout):
                    if status.status == "running" or (status.total > 0 and status.running >= status.total):
                        return
                raise Leap0Error("Desktop status stream ended without reaching 'running' state")
            except Leap0TimeoutError as exc:
                raise Leap0TimeoutError(f"Desktop did not become ready within {timeout:.0f}s: {exc}") from exc
            except Leap0Error as exc:
                last_error = exc
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise Leap0TimeoutError(
                        f"Desktop did not become ready within {timeout:.0f}s: {exc}"
                    ) from exc
                await asyncio.sleep(min(delay, remaining))
                delay = min(delay * 2, 5.0)
        if last_error is not None:
            raise Leap0TimeoutError(f"Desktop did not become ready within {timeout:.0f}s: {last_error}") from last_error
        raise Leap0TimeoutError(f"Desktop did not become ready within {timeout:.0f}s")


__all__ = ["AsyncDesktopClient"]
