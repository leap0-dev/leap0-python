from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import FileInfo, GitResult, Leap0Client, Sandbox, TreeResult


def main() -> None:
    client = Leap0Client()
    sandbox: Sandbox = client.sandboxes.create()
    repo_path = "/workspace/hello-world"

    try:
        clone: GitResult = sandbox.git.clone(
            url="https://github.com/octocat/Hello-World.git",
            path=repo_path,
            branch="master",
        )
        print("clone exit:", clone.exit_code)

        status: GitResult = sandbox.git.status(path=repo_path)
        print("git status:\n", status.output)

        sandbox.filesystem.write_file(
            path=f"{repo_path}/sdk-demo.txt",
            content="Hello from the Leap0 Python SDK\n",
        )
        print("file exists:", sandbox.filesystem.exists(path=f"{repo_path}/sdk-demo.txt"))

        file_info: FileInfo = sandbox.filesystem.stat(path=f"{repo_path}/README")
        print("readme size:", file_info.size)

        tree: TreeResult = sandbox.filesystem.tree(path=repo_path, max_depth=2)
        print("tree items:", [entry.name for entry in tree.items])
    finally:
        sandbox.delete()
        client.close()


if __name__ == "__main__":
    main()
