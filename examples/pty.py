from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from leap0 import Leap0Client, PtyConnection, PtySession, Sandbox


def main() -> None:
    client = Leap0Client()
    sandbox: Sandbox = client.sandboxes.create()

    try:
        session: PtySession = sandbox.pty.create(
            session_id="demo-terminal",
            cols=120,
            rows=30,
            cwd="/home/user",
        )
        connection: PtyConnection = sandbox.pty.connect(session.id)
        try:
            connection.send("pwd\n")
            print(connection.recv().decode("utf-8", errors="replace"))
        finally:
            connection.close()
    finally:
        try:
            sandbox.delete()
        finally:
            client.close()


if __name__ == "__main__":
    main()
