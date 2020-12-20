from datetime import datetime


__all__ = ["create_datetime"]


def create_datetime(date_str: str) -> datetime:
    """Create a datetime object from an ISO 8601 date string."""
    return datetime.fromisoformat(date_str.strip())
