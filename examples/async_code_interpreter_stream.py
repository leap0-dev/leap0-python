from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import AsyncLeap0Client, AsyncSandbox, StreamEvent


async def main() -> None:
    async with AsyncLeap0Client() as client:
        sandbox: AsyncSandbox = await client.sandboxes.create()

        try:
            async for event in sandbox.code_interpreter.execute_stream(
                code="import time\nfor i in range(3):\n    print(f'async step {i}')\n    time.sleep(1)",
                language="python",
                timeout_ms=10_000,
            ):
                typed_event: StreamEvent = event
                print(typed_event)
        finally:
            await sandbox.delete()


if __name__ == "__main__":
    asyncio.run(main())
