from __future__ import annotations

import time
from queue import Empty, Queue
from threading import Thread
from collections.abc import Iterator
from typing import cast

import httpx
from tenacity import retry, retry_if_exception, stop_after_delay, wait_exponential

from .._internal.types import JsonObject
from ..models.desktop import (
    DesktopDisplayInfo,
    DesktopDisplayInfoDict,
    DesktopHealth,
    DesktopHealthDict,
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
    DesktopWindow,
    DesktopWindowsDict,
)
from ..models.sandbox import SandboxRef, sandbox_id_of
from ..models.errors import Leap0Error, Leap0TimeoutError
from .._utils.errors import intercept_errors
from .._utils.stream import iter_sse_events
from .._utils.url import sandbox_base_url
from ._transport import Transport


class DesktopClient:
    """Control a graphical Linux desktop inside a sandbox.
    
        Requires a sandbox created with the
        :data:`~leap0.constants.DEFAULT_DESKTOP_TEMPLATE_NAME`
        (``system/desktop:v0.1.0``) template.  Provides display info, screenshots,
        mouse/keyboard input, and screen recording.
        
    Attributes:
        None.
    """

    def __init__(self, transport: Transport, *, sandbox_domain: str | None = None):
        self._transport = transport
        self._sandbox_domain = sandbox_domain.strip("/") if sandbox_domain else None

    def _request(
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
        return self._transport.request_target(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    def _request_json(
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
        return self._transport.request_target_json(
            method,
            f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}{path}",
            params=params,
            json=json,
            expected_status=expected_status,
            timeout=http_timeout,
        )

    def desktop_url(self, sandbox: SandboxRef) -> str:
        """Build the browser URL for the noVNC desktop viewer.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        return f"{sandbox_base_url(sandbox_id_of(sandbox), self._sandbox_domain)}/"

    @intercept_errors("Failed to get display info: ")
    def display_info(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get display information (display name, width, height).
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopDisplayInfoDict, self._request_json("GET", sandbox, "/api/display"))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to get screen info: ")
    def screen(self, sandbox: SandboxRef) -> DesktopDisplayInfo:
        """Get the current screen resolution.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopDisplayInfoDict, self._request_json("GET", sandbox, "/api/display/screen"))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to resize screen: ")
    def resize_screen(self, sandbox: SandboxRef, *, width: int, height: int, http_timeout: float | None = None) -> DesktopDisplayInfo:
        """
                    Resize the virtual display (width: 320-7680, height: 320-4320).
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopDisplayInfoDict, self._request_json(
            "POST",
            sandbox,
            "/api/display/screen",
            json={"width": width, "height": height},
            http_timeout=http_timeout,
        ))
        return DesktopDisplayInfo.from_dict(data)

    @intercept_errors("Failed to list windows: ")
    def windows(self, sandbox: SandboxRef) -> list[DesktopWindow]:
        """List all open windows on the desktop.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopWindowsDict, self._request_json("GET", sandbox, "/api/display/windows"))
        return [DesktopWindow.from_dict(item) for item in data.get("items", [])]

    @intercept_errors("Failed to take screenshot: ")
    def screenshot(
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
        params: JsonObject = {}
        if image_format is not None:
            params["format"] = image_format
        if quality is not None:
            params["quality"] = quality
        if x is not None:
            params["x"] = x
        if y is not None:
            params["y"] = y
        if width is not None:
            params["width"] = width
        if height is not None:
            params["height"] = height
        response = self._request("GET", sandbox, "/api/screenshot", params=params or None, http_timeout=http_timeout)
        return response.content

    @intercept_errors("Failed to take screenshot: ")
    def screenshot_region(
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
        payload: JsonObject = {"x": x, "y": y, "width": width, "height": height}
        if image_format is not None:
            payload["format"] = image_format
        if quality is not None:
            payload["quality"] = quality
        response = self._request("POST", sandbox, "/api/screenshot/region", json=payload, http_timeout=http_timeout)
        return response.content

    @intercept_errors("Failed to get pointer position: ")
    def pointer_position(self, sandbox: SandboxRef) -> DesktopPointerPosition:
        """Get the current mouse pointer position.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopPointerPositionDict, self._request_json("GET", sandbox, "/api/input/position"))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to move pointer: ")
    def move_pointer(self, sandbox: SandboxRef, *, x: int, y: int, http_timeout: float | None = None) -> DesktopPointerPosition:
        """
                    Move the mouse pointer to the given coordinates.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopPointerPositionDict, self._request_json("POST", sandbox, "/api/input/move", json={"x": x, "y": y}, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to click: ")
    def click(
        self,
        sandbox: SandboxRef,
        *,
        x: int | None = None,
        y: int | None = None,
        button: int | None = None,
        http_timeout: float | None = None,
    ) -> DesktopPointerPosition:
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
        payload: JsonObject = {}
        if x is not None:
            payload["x"] = x
        if y is not None:
            payload["y"] = y
        if button is not None:
            payload["button"] = button
        data = cast(DesktopPointerPositionDict, self._request_json("POST", sandbox, "/api/input/click", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to drag: ")
    def drag(
        self,
        sandbox: SandboxRef,
        *,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        button: int | None = None,
        http_timeout: float | None = None,
    ) -> DesktopPointerPosition:
        """
                    Drag from one position to another.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        payload: JsonObject = {
            "from_x": from_x,
            "from_y": from_y,
            "to_x": to_x,
            "to_y": to_y,
        }
        if button is not None:
            payload["button"] = button
        data = cast(DesktopPointerPositionDict, self._request_json("POST", sandbox, "/api/input/drag", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to scroll: ")
    def scroll(self, sandbox: SandboxRef, *, direction: str, amount: int | None = None, http_timeout: float | None = None) -> DesktopPointerPosition:
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
        data = cast(DesktopPointerPositionDict, self._request_json("POST", sandbox, "/api/input/scroll", json=payload, http_timeout=http_timeout))
        return DesktopPointerPosition.from_dict(data)

    @intercept_errors("Failed to type text: ")
    def type_text(self, sandbox: SandboxRef, *, text: str) -> bool:
        """Type text using simulated keyboard input (max 50,000 characters).
        
        Args:
            sandbox: Sandbox ID or object.
            text: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        data = self._request_json("POST", sandbox, "/api/input/type", json={"text": text})
        return bool(data.get("ok", False))

    @intercept_errors("Failed to press key: ")
    def press_key(self, sandbox: SandboxRef, *, key: str, http_timeout: float | None = None) -> bool:
        """
                    Press a single key by X11 keysym name (e.g. ``"Return"``, ``"Escape"``).
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = self._request_json("POST", sandbox, "/api/input/press", json={"key": key}, http_timeout=http_timeout)
        return bool(data.get("ok", False))

    @intercept_errors("Failed to press hotkey: ")
    def hotkey(self, sandbox: SandboxRef, *, keys: list[str]) -> bool:
        """Press multiple keys simultaneously (e.g. ``["Control_L", "c"]``).
        
        Args:
            sandbox: Sandbox ID or object.
            keys: Parameter for this operation.
        
        Returns:
            object: Result returned by this operation.
        """
        data = self._request_json("POST", sandbox, "/api/input/hotkey", json={"keys": keys})
        return bool(data.get("ok", False))

    @intercept_errors("Failed to get recording status: ")
    def recording_status(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopRecordingStatus:
        """
                    Get the current screen recording status.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, self._request_json("GET", sandbox, "/api/recording", http_timeout=http_timeout))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to start recording: ")
    def start_recording(self, sandbox: SandboxRef) -> DesktopRecordingStatus:
        """Start recording the screen. Returns 409 if a recording is already active.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, self._request_json("POST", sandbox, "/api/recording/start", expected_status=201))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to stop recording: ")
    def stop_recording(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopRecordingStatus:
        """
                    Stop the active screen recording.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingStatusDict, self._request_json("POST", sandbox, "/api/recording/stop", http_timeout=http_timeout))
        return DesktopRecordingStatus.from_dict(data)

    @intercept_errors("Failed to list recordings: ")
    def recordings(self, sandbox: SandboxRef) -> list[DesktopRecordingSummary]:
        """List all screen recordings.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        raw = self._request_json("GET", sandbox, "/api/recordings")
        items = cast(list[DesktopRecordingSummaryDict], raw.get("items", []))
        return [DesktopRecordingSummary.from_dict(item) for item in items]

    @intercept_errors("Failed to get recording: ")
    def get_recording(self, sandbox: SandboxRef, recording_id: str, http_timeout: float | None = None) -> DesktopRecordingSummary:
        """
                    Get details for a single recording.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopRecordingSummaryDict, self._request_json("GET", sandbox, f"/api/recordings/{recording_id}", http_timeout=http_timeout))
        return DesktopRecordingSummary.from_dict(data)

    @intercept_errors("Failed to download recording: ")
    def download_recording(self, sandbox: SandboxRef, recording_id: str) -> bytes:
        """Download a recording as MP4 bytes.
        
        Args:
            sandbox: Sandbox ID or object.
            recording_id: Recording identifier.
        
        Returns:
            object: Result returned by this operation.
        """
        response = self._request("GET", sandbox, f"/api/recordings/{recording_id}/download")
        return response.content

    @intercept_errors("Failed to delete recording: ")
    def delete_recording(self, sandbox: SandboxRef, recording_id: str, http_timeout: float | None = None) -> None:
        """
            Delete a recording. Cannot delete an active recording.

            Args:
            http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        """
        self._request("DELETE", sandbox, f"/api/recordings/{recording_id}", expected_status=204, http_timeout=http_timeout)

    @intercept_errors("Failed to check desktop health: ")
    def health(self, sandbox: SandboxRef) -> DesktopHealth:
        """Check the health of the desktop environment.
        
        Args:
            sandbox: Sandbox ID or object.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopHealthDict, self._request_json("GET", sandbox, "/api/healthz", expected_status=(200, 503)))
        return DesktopHealth.from_dict(data)

    @intercept_errors("Failed to get process status: ")
    def process_status(self, sandbox: SandboxRef, http_timeout: float | None = None) -> DesktopProcessStatusList:
        """
                    Get the status of all desktop processes (xvfb, xfce4, x11vnc, novnc).
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessStatusListDict, self._request_json("GET", sandbox, "/api/status", http_timeout=http_timeout))
        return DesktopProcessStatusList.from_dict(data)

    @intercept_errors("Failed to get process: ")
    def get_process(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessStatus:
        """Get the status of a single desktop process by name.
        
        Args:
            sandbox: Sandbox ID or object.
            process_name: Desktop process name.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessStatusDict, self._request_json("GET", sandbox, f"/api/process/{process_name}/status"))
        return DesktopProcessStatus.from_dict(data)

    @intercept_errors("Failed to restart process: ")
    def restart_process(self, sandbox: SandboxRef, process_name: str, http_timeout: float | None = None) -> DesktopProcessRestart:
        """
                    Restart a desktop process.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessRestartDict, self._request_json("POST", sandbox, f"/api/process/{process_name}/restart", http_timeout=http_timeout))
        return DesktopProcessRestart.from_dict(data)

    @intercept_errors("Failed to get process logs: ")
    def process_logs(self, sandbox: SandboxRef, process_name: str) -> DesktopProcessLogs:
        """Get stdout logs for a desktop process.
        
        Args:
            sandbox: Sandbox ID or object.
            process_name: Desktop process name.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessLogsDict, self._request_json("GET", sandbox, f"/api/process/{process_name}/logs"))
        return DesktopProcessLogs.from_dict(data)

    @intercept_errors("Failed to get process errors: ")
    def process_errors(self, sandbox: SandboxRef, process_name: str, http_timeout: float | None = None) -> DesktopProcessErrors:
        """
                    Get stderr logs for a desktop process.
        
                    Args:
                    http_timeout: Optional HTTP request timeout in seconds for this SDK call.
        
        Returns:
            object: Result returned by this operation.
        """
        data = cast(DesktopProcessErrorsDict, self._request_json("GET", sandbox, f"/api/process/{process_name}/errors", http_timeout=http_timeout))
        return DesktopProcessErrors.from_dict(data)

    @intercept_errors("Failed to stream status: ")
    def status_stream(self, sandbox: SandboxRef, *, deadline: float | None = None, http_timeout: float | None = None) -> Iterator[DesktopProcessStatusList]:
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
        response = self._transport.stream("GET", url, timeout=stream_timeout)
        try:
            events = iter_sse_events(response.iter_lines())

            def _next_event(timeout: float | None) -> object:
                result: Queue[tuple[str, object]] = Queue(maxsize=1)

                def _read_event() -> None:
                    try:
                        result.put(("event", next(events)))
                    except StopIteration as exc:
                        result.put(("stop", exc))
                    except BaseException as exc:  # pragma: no cover - passthrough guard
                        result.put(("error", exc))

                reader = Thread(target=_read_event, daemon=True)
                reader.start()
                try:
                    kind, value = result.get(timeout=timeout)
                except Empty as exc:
                    raise Leap0TimeoutError("Desktop status stream timed out") from exc
                if kind == "event":
                    return value
                if kind == "stop":
                    raise cast(StopIteration, value)
                raise cast(BaseException, value)

            while True:
                read_timeout = http_timeout
                if deadline is not None:
                    remaining_time = deadline - time.monotonic()
                    if remaining_time <= 0:
                        raise Leap0TimeoutError("Desktop status stream timed out")
                    read_timeout = remaining_time if read_timeout is None else min(read_timeout, remaining_time)
                try:
                    event = _next_event(read_timeout)
                except StopIteration:
                    break
                if not isinstance(event, dict):
                    raise ValueError(
                        "Malformed desktop status stream event "
                        f"for sandbox={sandbox_id_of(sandbox)!r}, source='status_stream': {event!r}"
                    )
                # Explicit error envelope from the server.
                if "error" in event:
                    raise Leap0Error(
                        "Desktop status stream error",
                        body=str(event["error"]),
                    )
                yield DesktopProcessStatusList.from_dict(cast(DesktopProcessStatusListDict, event))
        finally:
            response.close()

    def wait_until_ready(self, sandbox: SandboxRef, *, timeout: float = 60.0, http_timeout: float | None = None) -> None:
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

        def _is_transient_leap0(exc: BaseException) -> bool:
            """Return True only for retryable Leap0 errors."""
            return isinstance(exc, Leap0Error) and not isinstance(exc, Leap0TimeoutError) and exc.retryable

        deadline = time.monotonic() + timeout

        @retry(
            stop=stop_after_delay(timeout),
            wait=wait_exponential(multiplier=0.5, min=0.5, max=5),
            retry=retry_if_exception(_is_transient_leap0),
            reraise=True,
        )
        def _poll() -> None:
            for status in self.status_stream(sandbox, deadline=deadline, http_timeout=http_timeout):
                if status.status == "running":
                    return
            raise Leap0Error("Desktop status stream ended without reaching 'running' state", retryable=True)

        try:
            _poll()
        except Leap0TimeoutError as exc:
            raise Leap0TimeoutError(
                f"Desktop did not become ready within {timeout:.0f}s: {exc}"
            ) from exc
        except Leap0Error as exc:
            if exc.retryable:
                raise Leap0TimeoutError(
                    f"Desktop did not become ready within {timeout:.0f}s: {exc}"
                ) from exc
            raise
