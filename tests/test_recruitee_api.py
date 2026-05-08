from unittest.mock import Mock

from ClashRecruit.api.recruitee_api import Recruitee
from constants import KNOWN_STABLE_TAG, MOCK_HEADERS


def test_search_clan_success_without_after(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)
    filters = {"name": "test_filter"}

    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "items": [{"tag": "#ABC"}],
        "paging": {"cursors": {"after": "cursor-1"}},
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruitee_api.requests.get",
        mock_get,
    )

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
        timeout=10,
    )


def test_search_clan_includes_after_cursor_in_params(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)
    filters = {"name": "test_filter"}

    fake_response = Mock()
    fake_response.status_code = 200
    fake_response.json.return_value = {"items": []}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruitee_api.requests.get",
        mock_get,
    )

    result = user.searchClan(filters, after="next-cursor")

    assert result["items"] == []
    assert result["after"] is None
    assert result["error"] is None
    assert filters["after"] == "next-cursor"
    mock_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/clans",
        params={"name": "test_filter", "after": "next-cursor"},
        headers=MOCK_HEADERS,
        timeout=10,
    )


def test_search_clan_maps_api_error_payload(monkeypatch) -> None:
    user = Recruitee(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.status_code = 400
    fake_response.json.return_value = {
        "reason": "badRequest",
        "message": "At least one filtering parameter must exist",
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruitee_api.requests.get",
        mock_get,
    )

    result = user.searchClan({})

    assert result["items"] == []
    assert result["after"] is None
    assert result["error"] == {
        "reason": "badRequest",
        "message": "At least one filtering parameter must exist",
        "status": 400,
    }
