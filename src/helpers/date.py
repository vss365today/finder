from datetime import datetime


__all__ = ["create_datetime", "format_datetime", "create_api_date"]


def create_datetime(date_str: str) -> datetime:
    """Create a datetime object from an ISO date string."""
    return datetime.strptime(date_str.strip(), "%Y-%m-%d")


def format_datetime(date_obj: datetime) -> str:
    """Format a datetime object as YYYY-MM-DD."""
    return date_obj.strftime("%Y-%m-%d")


def create_api_date(date_str: str) -> datetime:
    """Create a datetime object from an API response date string.
    E.g, Tue, 02 Jul 2019 00:00:00 GMT
    """
    return datetime.strptime(date_str.strip(), "%a, %d %b %Y 00:00:00 GMT")
