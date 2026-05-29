"""Shared HTTP client helpers for the Clash of Clans API."""

from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import requests

BASE_URL = "https://api.clashofclans.com/v1/"
DEFAULT_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class ClashApiResponse:
    """Parsed Clash API response metadata."""

    status_code: int
    payload: dict[str, Any]


class ClashApiError(Exception):
    """Base error raised for Clash API request failures."""


class ClashApiNetworkError(ClashApiError):
    """Raised when the request fails before a response is available."""


class ClashApiJSONError(ClashApiError):
    """Raised when the Clash API response body is not valid JSON."""


class ClashApiHTTPError(ClashApiError):
    """Raised when the Clash API returns an unexpected HTTP status."""

    def __init__(
        self,
        status_code: int,
        payload: dict[str, Any],
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.reason = payload.get("reason", "unknown")
        self.message = payload.get("message")
        super().__init__(f"HTTP {status_code}: {self.reason}")


def get(
    path: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    allowed_statuses: set[int] | None = None,
) -> ClashApiResponse:
    """Send a GET request to the Clash API and return parsed JSON."""
    return _request(
        "GET",
        path,
        headers=headers,
        params=params,
        timeout=timeout,
        allowed_statuses=allowed_statuses,
    )


def post(
    path: str,
    *,
    headers: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    allowed_statuses: set[int] | None = None,
) -> ClashApiResponse:
    """Send a POST request to the Clash API and return parsed JSON."""
    return _request(
        "POST",
        path,
        headers=headers,
        json=json,
        timeout=timeout,
        allowed_statuses=allowed_statuses,
    )


def _request(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    allowed_statuses: set[int] | None = None,
) -> ClashApiResponse:
    """Send an HTTP request with shared Clash API handling."""
    allowed_statuses = allowed_statuses or set()
    try:
        response = requests.request(
            method,
            _build_url(path),
            headers=headers,
            params=params,
            json=json,
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise ClashApiNetworkError(str(exc)) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ClashApiJSONError(
            "Clash API response was not valid JSON"
        ) from exc

    if (
        response.status_code >= 400
        and response.status_code not in allowed_statuses
    ):
        raise ClashApiHTTPError(response.status_code, payload)

    return ClashApiResponse(status_code=response.status_code, payload=payload)


def _build_url(path: str) -> str:
    """Return an absolute Clash API URL for relative endpoint paths."""
    if path.startswith(("http://", "https://")):
        return path
    return urljoin(BASE_URL, path.lstrip("/"))
