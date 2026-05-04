from unittest.mock import Mock

from ClashRecruit.api.recruiter_api import Recruiter
from constants import KNOWN_STABLE_TAG, MOCK_HEADERS


def test_pull_clan_requirements_success(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "items": [
            {
                "requiredTownhallLevel": 12,
                "requiredBuilderBaseTrophies": 2300,
            }
        ]
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        mock_get,
    )

    requirements = user.pull_clan_requirements()

    assert requirements == [0, 2300, 12]
    mock_get.assert_called_once_with(
        f"https://api.clashofclans.com/v1/clans?name=%23{KNOWN_STABLE_TAG}",
        headers=MOCK_HEADERS,
    )


def test_pull_clan_requirements_defaults_when_api_returns_no_items(
    monkeypatch,
) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"items": []}
    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        Mock(return_value=fake_response),
    )

    assert user.pull_clan_requirements() == [0, 0, 0]


def test_pull_clan_requirements_defaults_when_items_missing(
    monkeypatch,
) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {}
    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        Mock(return_value=fake_response),
    )

    assert user.pull_clan_requirements() == [0, 0, 0]


def test_lookup_clan_full_payload(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "name": "Test Clan",
        "type": "inviteOnly",
        "description": "Friendly and active",
        "location": {"id": 32000007, "name": "Canada"},
        "badgeUrls": {"medium": "badge-medium-url"},
        "clanLevel": 14,
        "members": 40,
        "warFrequency": "always",
        "clanPoints": 42000,
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        mock_get,
    )

    result = user.lookup_clan()

    assert result == {
        "name": "Test Clan",
        "type": "inviteOnly",
        "description": "Friendly and active",
        "location": {"id": 32000007, "name": "Canada"},
        "badge": "badge-medium-url",
        "clan_level": 14,
        "member_count": 40,
        "warFrequency": "always",
        "clanPoints": 42000,
    }
    mock_get.assert_called_once_with(
        f"https://api.clashofclans.com/v1/clans/%23{KNOWN_STABLE_TAG}",
        headers=MOCK_HEADERS,
    )


def test_lookup_clan_member_count_mode(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"members": 48}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        mock_get,
    )

    result = user.lookup_clan("member_count")

    assert result == {"member_count": 48}


def test_lookup_clan_description_mode(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"description": "War focused clan"}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.recruiter_api.requests.get",
        mock_get,
    )

    result = user.lookup_clan("description")

    assert result == {"description": "War focused clan"}
