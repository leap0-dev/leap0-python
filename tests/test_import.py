from leap0 import Leap0Client


def test_client_import() -> None:
    client = Leap0Client(api_key="test")
    client.close()
