from typing import Any, Union

import requests
import sys_vars


__all__ = ["get", "post"]


def __create_api_url(*args: str) -> str:
    """Construct a URL to the given API endpoint."""
    endpoint = "/".join(args)
    return f"{sys_vars.get('API_DOMAIN')}/{endpoint}/"


def get(*args: str, **kwargs: Any) -> Union[list, dict]:
    """Helper function for performing a GET request."""
    url = __create_api_url(*args)
    r = requests.get(url, **kwargs)
    r.raise_for_status()
    return r.json() if r.text else {}


def post(*args: str, **kwargs: Any) -> Union[list, dict]:
    """Helper function for performing a POST request."""
    url = __create_api_url(*args)
    r = requests.post(url, **kwargs)
    r.raise_for_status()
    return r.json() if r.text else {}
