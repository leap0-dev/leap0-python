from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import AsyncLeap0Client, AsyncSandbox, ProcessResult


async def main() -> None:
    async with AsyncLeap0Client() as client:
        sandbox: AsyncSandbox = await client.sandboxes.create()

        try:
            result: ProcessResult = await sandbox.process.execute(command="echo hello from async leap0")
            print("sandbox:", sandbox.id)
            print("exit code:", result.exit_code)
            print("stdout:", result.stdout.strip())
            print("stderr:", result.stderr.strip())
        finally:
            await sandbox.delete()


if __name__ == "__main__":
    asyncio.run(main())
