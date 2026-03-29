from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0, Leap0Config


def main() -> None:
    client = Leap0(Leap0Config())
    sandbox = client.sandboxes.create()

    try:
        session = client.pty.create(
            sandbox,
            session_id="demo-terminal",
            cols=120,
            rows=30,
            cwd="/home/user",
        )
        connection = client.pty.connect(sandbox, session.id)
        try:
            connection.send("pwd\n")
            print(connection.recv().decode("utf-8", errors="replace"))
        finally:
            connection.close()
    finally:
        client.sandboxes.delete(sandbox)
        client.close()


if __name__ == "__main__":
    main()
