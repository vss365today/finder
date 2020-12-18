from datetime import datetime


__all__ = ["create_datetime", "format_datetime"]


def create_datetime(date_str: str) -> datetime:
    """Create a datetime object from an ISO 8601 date string."""
    return datetime.fromisoformat(date_str.strip())


def format_datetime(datetime_obj: datetime) -> str:
    """Format a datetime object as YYYY-MM-DD."""
    return datetime_obj.strftime("%Y-%m-%d")
