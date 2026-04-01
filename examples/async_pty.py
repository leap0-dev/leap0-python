from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import AsyncLeap0Client, AsyncPtyConnection, AsyncSandbox, PtySession


async def main() -> None:
    async with AsyncLeap0Client() as client:
        sandbox: AsyncSandbox = await client.sandboxes.create()

        try:
            session: PtySession = await sandbox.pty.create(
                session_id="async-demo-terminal",
                cols=120,
                rows=30,
                cwd="/home/user",
            )
            connection: AsyncPtyConnection = await sandbox.pty.connect(session.id)
            try:
                await connection.send("pwd\n")
                print((await connection.recv()).decode("utf-8", errors="replace"))
            finally:
                await connection.close()
        finally:
            await sandbox.delete()


if __name__ == "__main__":
    asyncio.run(main())
