import time
from json import JSONDecodeError
from typing import Any, Optional
from urllib.parse import urljoin

import requests

from aleksis.core.util.core_helpers import get_site_preferences


class MatrixException(Exception):
    pass


def build_url(path: str) -> str:
    """Build a URL to the Matrix Client Server API."""
    return urljoin(
        urljoin(get_site_preferences()["matrix__homeserver"], "_matrix/client/v3/"), path
    )


def get_headers() -> dict[str, str]:
    """Get the headers for a Matrix Client Server API request."""
    return {
        "Authorization": "Bearer " + get_site_preferences()["matrix__access_token"],
    }


def do_matrix_request(method: str, url: str, body: Optional[dict] = None) -> dict[str, Any]:
    """Do a HTTP request to the Matrix Client Server API."""
    while True:
        res = requests.request(method=method, url=build_url(url), headers=get_headers(), json=body)  # noqa: S113

        try:
            data = res.json()
        except JSONDecodeError:
            raise MatrixException(res.text) from JSONDecodeError

        if res.status_code == requests.codes.ok:
            break

        # If rate limit exceeded, wait and retry
        if data.get("errcode", "") == "M_LIMIT_EXCEEDED":
            time.sleep(data["retry_after_ms"] / 1000)
        else:
            raise MatrixException(data)

    return data
