from functools import partial
from typing import Any, Callable

import httpx
import sys_vars


__all__ = ["delete", "get", "post", "put"]


def __create_auth_token() -> dict:
    """Create HTTP header for accessing protected API endpoints."""
    return {"Authorization": f"Bearer {sys_vars.get('API_AUTH_TOKEN')}"}


def __make_request(method: Callable, url: str, **kwargs: Any) -> dict:
    """Make a request to the API."""
    kwargs["headers"] = __create_auth_token()
    kwargs["timeout"] = None
    r = method(url=url, **kwargs)
    r.raise_for_status()
    return r.json() if r.text else {}


def delete(url: str, **kwargs: Any) -> dict:
    """Helper function for performing a DELETE request."""
    func = partial(httpx.request, method="DELETE")
    func.__name__ = "delete"
    return __make_request(func, url, **kwargs)


def get(url: str, **kwargs: Any) -> dict:
    """Helper function for performing a GET request."""
    return __make_request(httpx.get, url, **kwargs)


def post(url: str, **kwargs: Any) -> dict:
    """Helper function for performing a POST request."""
    return __make_request(httpx.post, url, **kwargs)


def put(url: str, **kwargs: Any) -> dict:
    """Helper function for performing a PUT request."""
    return __make_request(httpx.put, url, **kwargs)
