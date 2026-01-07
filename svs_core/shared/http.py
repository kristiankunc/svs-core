import re

from typing import Optional

import httpx

from svs_core.shared.logger import get_logger


def send_http_request(
    method: str,
    url: str,
    headers: Optional[dict[str, str]] = None,
    params: Optional[dict[str, str]] = None,
    data: Optional[dict[str, str]] = None,
    json: Optional[dict[str, object]] = None,
) -> httpx.Response:
    """Sends an HTTP request and returns the response.

    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE).
        url (str): The URL to send the request to.
        headers (dict, optional): Headers to include in the request.
        params (dict, optional): Query parameters for the request.
        data (dict, optional): Form data to include in the request.
        json (dict, optional): JSON data to include in the request.

    Returns:
        httpx.Response: The response object containing the server's response.
    """
    get_logger(__name__).debug(
        f"Sending {method} request to {url} with headers={headers}, params={params}, data={data}, json={json}"
    )
    with httpx.Client() as client:
        response = client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            data=data,
            json=json,
        )

        get_logger(__name__).debug(
            f"Received response: {response.status_code} {response.text}"
        )

        response.raise_for_status()
        return response


def is_url(url: str) -> bool:
    """Check if a string is a valid URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the string is a valid URL, False otherwise.
    """
    # Matches http(s)://hostname with optional port, path, query, and fragment
    # Supports domains with dots, localhost, and IP addresses
    url_regex = re.compile(
        r"https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}(\.[a-zA-Z0-9()]{1,6})?\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)"
    )
    return re.match(url_regex, url) is not None
