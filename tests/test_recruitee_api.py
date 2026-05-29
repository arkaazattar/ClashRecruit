from unittest.mock import Mock

import ClashRecruit.api.recruitee_api as recruitee_api
from ClashRecruit.api.recruitee_api import Recruitee
from ClashRecruit.clash_http_client import ClashApiHTTPError, ClashApiResponse
from constants import KNOWN_STABLE_TAG, MOCK_HEADERS


def test_search_clan_success_without_after(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)
    filters = {"name": "test_filter"}

    fake_response = ClashApiResponse(
        200,
        {
            "items": [{"tag": "#ABC"}],
            "paging": {"cursors": {"after": "cursor-1"}},
        },
    )
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruitee_api, "clash_get", mock_get)

    result = user.searchClan(filters)

    assert result == {
        "items": [{"tag": "#ABC"}],
        "after": "cursor-1",
        "error": None,
    }
    mock_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/clans",
        params={"name": "test_filter"},
        headers=MOCK_HEADERS,
    )


def test_search_clan_includes_after_cursor_in_params(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)
    filters = {"name": "test_filter"}

    fake_response = ClashApiResponse(200, {"items": []})
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruitee_api, "clash_get", mock_get)

    result = user.searchClan(filters, after="next-cursor")

    assert result["items"] == []
    assert result["after"] is None
    assert result["error"] is None
    assert filters["after"] == "next-cursor"
    mock_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/clans",
        params={"name": "test_filter", "after": "next-cursor"},
        headers=MOCK_HEADERS,
    )


def test_search_clan_maps_api_error_payload(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)

    mock_get = Mock(
        side_effect=ClashApiHTTPError(
            400,
            {
                "reason": "badRequest",
                "message": "At least one filtering parameter must exist",
            },
        )
    )

    monkeypatch.setattr(recruitee_api, "clash_get", mock_get)

    result = user.searchClan({})

    assert result["items"] == []
    assert result["after"] is None
    assert result["error"] == {
        "reason": "badRequest",
        "message": "At least one filtering parameter must exist",
        "status": 400,
    }
