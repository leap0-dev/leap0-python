from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import AsyncLeap0Client, AsyncSandbox, CodeExecutionResult


async def main() -> None:
    async with AsyncLeap0Client() as client:
        sandbox: AsyncSandbox = await client.sandboxes.create()

        try:
            result: CodeExecutionResult = await sandbox.code_interpreter.execute(
                code="print('hello from async leap0')",
                language="python",
            )
            print("sandbox:", sandbox.id)
            print("result:", result.main_text)
        finally:
            await sandbox.delete()


if __name__ == "__main__":
    asyncio.run(main())
