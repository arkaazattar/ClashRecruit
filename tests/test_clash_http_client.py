from unittest.mock import Mock

import pytest
import requests
from ClashRecruit import clash_http_client
from ClashRecruit.clash_http_client import (
    ClashApiHTTPError,
    ClashApiJSONError,
    ClashApiNetworkError,
)


def test_get_uses_base_url_headers_params_and_default_timeout(monkeypatch):
    fake_response = Mock(status_code=200)
    fake_response.json.return_value = {"items": []}
    fake_request = Mock(return_value=fake_response)
    monkeypatch.setattr(clash_http_client.requests, "request", fake_request)

    result = clash_http_client.get(
        "/clans",
        headers={"Authorization": "Bearer token"},
        params={"name": "test"},
    )

    assert result.payload == {"items": []}
    fake_request.assert_called_once_with(
        "GET",
        "https://api.clashofclans.com/v1/clans",
        headers={"Authorization": "Bearer token"},
        params={"name": "test"},
        json=None,
        timeout=10,
    )


def test_post_sends_json_body(monkeypatch):
    fake_response = Mock(status_code=200)
    fake_response.json.return_value = {"status": "ok"}
    fake_request = Mock(return_value=fake_response)
    monkeypatch.setattr(clash_http_client.requests, "request", fake_request)

    result = clash_http_client.post(
        "players/%23PLAYER/verifytoken",
        headers={"Authorization": "Bearer token"},
        json={"token": "abc"},
    )

    assert result.payload == {"status": "ok"}
    fake_request.assert_called_once_with(
        "POST",
        "https://api.clashofclans.com/v1/players/%23PLAYER/verifytoken",
        headers={"Authorization": "Bearer token"},
        params=None,
        json={"token": "abc"},
        timeout=10,
    )


def test_http_error_includes_status_and_payload(monkeypatch):
    fake_response = Mock(status_code=403)
    fake_response.json.return_value = {
        "reason": "accessDenied.invalidIp",
        "message": "Invalid IP",
    }
    monkeypatch.setattr(
        clash_http_client.requests,
        "request",
        Mock(return_value=fake_response),
    )

    with pytest.raises(ClashApiHTTPError) as error:
        clash_http_client.get("locations")

    assert error.value.status_code == 403
    assert error.value.reason == "accessDenied.invalidIp"
    assert error.value.message == "Invalid IP"
    assert error.value.payload == fake_response.json.return_value


def test_allowed_http_status_returns_response(monkeypatch):
    fake_response = Mock(status_code=404)
    fake_response.json.return_value = {"reason": "notFound"}
    monkeypatch.setattr(
        clash_http_client.requests,
        "request",
        Mock(return_value=fake_response),
    )

    result = clash_http_client.get("clans/%23MISSING", allowed_statuses={404})

    assert result.status_code == 404
    assert result.payload == {"reason": "notFound"}


def test_invalid_json_raises_normalized_error(monkeypatch):
    fake_response = Mock(status_code=200)
    fake_response.json.side_effect = ValueError("no json")
    monkeypatch.setattr(
        clash_http_client.requests,
        "request",
        Mock(return_value=fake_response),
    )

    with pytest.raises(ClashApiJSONError):
        clash_http_client.get("locations")


def test_request_exception_raises_normalized_network_error(monkeypatch):
    monkeypatch.setattr(
        clash_http_client.requests,
        "request",
        Mock(side_effect=requests.Timeout("timed out")),
    )

    with pytest.raises(ClashApiNetworkError):
        clash_http_client.get("locations")
