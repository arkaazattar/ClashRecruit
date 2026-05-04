from unittest.mock import Mock

import ClashRecruit.services.clash_api_preflight as preflight
import pytest


def test_run_clash_api_preflight_returns_for_success(monkeypatch):
    fake_response = Mock(status_code=200)
    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(preflight.requests, "get", fake_get)

    result = preflight.run_clash_api_preflight({"Authorization": "token"})

    assert result is None
    fake_get.assert_called_once_with(
        (
            "https://api.clashofclans.com/v1/locations/32000249/"
            "rankings/players?limit=1"
        ),
        headers={"Authorization": "token"},
    )


def test_run_clash_api_preflight_raises_for_api_error(monkeypatch):
    fake_response = Mock(status_code=403)
    fake_response.json.return_value = {"reason": "accessDenied.invalidIp"}
    monkeypatch.setattr(
        preflight.requests,
        "get",
        Mock(return_value=fake_response),
    )

    with pytest.raises(Exception, match="HTTP 403: accessDenied.invalidIp"):
        preflight.run_clash_api_preflight({"Authorization": "token"})


def test_run_clash_api_preflight_uses_unknown_reason_fallback(monkeypatch):
    fake_response = Mock(status_code=500)
    fake_response.json.return_value = {}
    monkeypatch.setattr(
        preflight.requests,
        "get",
        Mock(return_value=fake_response),
    )

    with pytest.raises(Exception, match="HTTP 500: unknown"):
        preflight.run_clash_api_preflight({"Authorization": "token"})
