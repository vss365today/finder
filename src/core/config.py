from json import loads
from pathlib import Path


__all__ = ["load"]


def load() -> dict:
    """Load the app config values from file."""
    return loads((Path("configuration") / "default.json").read_text())
