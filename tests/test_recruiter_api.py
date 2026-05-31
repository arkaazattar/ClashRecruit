from unittest.mock import Mock

import ClashRecruit.api.recruiter_api as recruiter_api
from ClashRecruit.api.recruiter_api import Recruiter
from ClashRecruit.clash_http_client import ClashApiResponse
from constants import KNOWN_STABLE_TAG, MOCK_HEADERS


def test_pull_clan_requirements_success(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = ClashApiResponse(
        200,
        {
            "requiredTownhallLevel": 12,
            "requiredBuilderBaseTrophies": 2300,
        },
    )
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruiter_api, "clash_get", mock_get)

    requirements = user.pull_clan_requirements()

    assert requirements == [0, 2300, 12]
    mock_get.assert_called_once_with(
        f"https://api.clashofclans.com/v1/clans/%23{KNOWN_STABLE_TAG}",
        headers=MOCK_HEADERS,
    )


def test_pull_clan_requirements_defaults_when_payload_is_empty(
    monkeypatch,
) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    monkeypatch.setattr(
        recruiter_api,
        "clash_get",
        Mock(return_value=ClashApiResponse(200, {})),
    )

    assert user.pull_clan_requirements() == [0, 0, 0]


def test_pull_clan_requirements_defaults_when_payload_is_malformed(
    monkeypatch,
) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    monkeypatch.setattr(
        recruiter_api,
        "clash_get",
        Mock(return_value=ClashApiResponse(200, [])),
    )

    assert user.pull_clan_requirements() == [0, 0, 0]


def test_extract_clan_requirements_defaults_missing_values() -> None:
    assert recruiter_api.extract_clan_requirements({}) == [0, 0, 0]


def test_extract_clan_requirements_defaults_malformed_payloads() -> None:
    assert recruiter_api.extract_clan_requirements(None) == [0, 0, 0]
    assert recruiter_api.extract_clan_requirements([]) == [0, 0, 0]


def test_lookup_clan_full_payload(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = ClashApiResponse(
        200,
        {
            "name": "Test Clan",
            "type": "inviteOnly",
            "description": "Friendly and active",
            "location": {"id": 32000007, "name": "Canada"},
            "badgeUrls": {"medium": "badge-medium-url"},
            "clanLevel": 14,
            "members": 40,
            "warFrequency": "always",
            "clanPoints": 42000,
        },
    )
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruiter_api, "clash_get", mock_get)

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

    fake_response = ClashApiResponse(200, {"members": 48})
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruiter_api, "clash_get", mock_get)

    result = user.lookup_clan("member_count")

    assert result == {"member_count": 48}


def test_lookup_clan_description_mode(monkeypatch) -> None:
    user = Recruiter(KNOWN_STABLE_TAG, MOCK_HEADERS)

    fake_response = ClashApiResponse(200, {"description": "War focused clan"})
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(recruiter_api, "clash_get", mock_get)

    result = user.lookup_clan("description")

    assert result == {"description": "War focused clan"}
