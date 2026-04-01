from importlib.metadata import PackageNotFoundError, version

try:
    SDK_VERSION = version("leap0")
except PackageNotFoundError:
    SDK_VERSION = "unknown"
