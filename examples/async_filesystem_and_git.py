from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import AsyncLeap0Client, AsyncSandbox, FileInfo, GitResult, TreeResult


async def main() -> None:
    async with AsyncLeap0Client() as client:
        sandbox: AsyncSandbox = await client.sandboxes.create()
        repo_path = "/workspace/hello-world"

        try:
            clone: GitResult = await sandbox.git.clone(
                url="https://github.com/octocat/Hello-World.git",
                path=repo_path,
                branch="master",
            )
            print("clone exit:", clone.exit_code)

            status: GitResult = await sandbox.git.status(path=repo_path)
            print("git status:\n", status.output)

            await sandbox.filesystem.write_file(
                path=f"{repo_path}/async-demo.txt",
                content="Hello from the async Leap0 Python SDK\n",
            )

            file_info: FileInfo = await sandbox.filesystem.stat(path=f"{repo_path}/README")
            print("readme size:", file_info.size)

            tree: TreeResult = await sandbox.filesystem.tree(path=repo_path, max_depth=2)
            print("tree items:", [entry.name for entry in tree.items])
        finally:
            await sandbox.delete()


if __name__ == "__main__":
    asyncio.run(main())
