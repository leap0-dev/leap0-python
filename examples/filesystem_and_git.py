from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create()
    repo_path = "/workspace/hello-world"

    try:
        clone = client.git.clone(
            sandbox,
            url="https://github.com/octocat/Hello-World.git",
            path=repo_path,
            branch="master",
        )
        print("clone exit:", clone.exit_code)

        status = client.git.status(sandbox, path=repo_path)
        print("git status:\n", status.output)

        client.filesystem.write_file_text(
            sandbox,
            path=f"{repo_path}/sdk-demo.txt",
            content="Hello from the Leap0 Python SDK\n",
        )
        print("file exists:", client.filesystem.exists(sandbox, path=f"{repo_path}/sdk-demo.txt"))

        tree = client.filesystem.tree(sandbox, path=repo_path, max_depth=2)
        print("tree items:", [entry.name for entry in tree.items])
    finally:
        client.sandboxes.delete(sandbox)
        client.close()


if __name__ == "__main__":
    main()
