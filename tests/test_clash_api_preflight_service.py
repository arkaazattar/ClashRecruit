from unittest.mock import Mock

import ClashRecruit.services.clash_api_preflight as preflight
import pytest
from ClashRecruit.clash_http_client import ClashApiHTTPError, ClashApiResponse


def test_run_clash_api_preflight_returns_for_success(monkeypatch):
    fake_get = Mock(return_value=ClashApiResponse(200, {"items": []}))
    monkeypatch.setattr(preflight, "clash_get", fake_get)

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
    monkeypatch.setattr(
        preflight,
        "clash_get",
        Mock(
            side_effect=ClashApiHTTPError(
                403,
                {"reason": "accessDenied.invalidIp"},
            )
        ),
    )

    with pytest.raises(Exception, match="HTTP 403: accessDenied.invalidIp"):
        preflight.run_clash_api_preflight({"Authorization": "token"})


def test_run_clash_api_preflight_uses_unknown_reason_fallback(monkeypatch):
    monkeypatch.setattr(
        preflight,
        "clash_get",
        Mock(side_effect=ClashApiHTTPError(500, {})),
    )

    with pytest.raises(Exception, match="HTTP 500: unknown"):
        preflight.run_clash_api_preflight({"Authorization": "token"})
