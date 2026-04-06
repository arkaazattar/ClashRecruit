from unittest.mock import Mock

import pytest
from ClashRecruit.api.clash_api import API
from constants import KNOWN_STABLE_TAG, MOCK_HEADERS


def test_player_api_is_false(monkeypatch) -> None:
    user = API(KNOWN_STABLE_TAG, api="invalid-token", headers=MOCK_HEADERS)
    fake_response = Mock()
    fake_response.json.return_value = {"status": "invalid"}
    mock_post = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.post",
        mock_post,
    )

    assert user.check_player_api() is False
    assert user.reason == "API Token is incorrect"


def test_player_is_guest() -> None:
    guest_user = API("Guest", None, None)
    guest_user.check_player()

    assert guest_user.user_tag == "Guest"
    assert guest_user.reason == "User is a Guest"


def test_player_not_found(monkeypatch) -> None:
    invalid_user = API("INVALID_TAG", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"reason": "notFound"}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    assert not invalid_user.check_player()
    assert invalid_user.reason == "Player tag is incorrect"


def test_invalid_ip_address(monkeypatch) -> None:
    user = API("invalid_ip_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"reason": "accessDenied.invalidIp"}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    assert not user.check_player()
    assert user.reason == "Invalid IP"


def test_player_api_is_true(monkeypatch) -> None:
    user = API("valid_user", api="valid-token", headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"status": "ok"}
    mock_post = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.post",
        mock_post,
    )

    assert user.check_player_api()


def test_check_player_with_all_request_options(monkeypatch) -> None:
    user = API("valid_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "leagueTier": {"name": "Unranked"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "townHallWeaponLevel": 5,
        "expLevel": 100,
        "builderBaseLeague": {
            "id": 44000033,
            "name": "Platinum League II",
        },
        "builderHallLevel": 9,
        "clan": {"tag": "#mock_clan_tag"},
        "role": "coLeader",
        "name": "valid_user",
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    result = user.check_player([
        "expLevel",
        "leagueTier",
        "builderBaseLeague",
        "builderHallLevel",
        "clan",
    ])

    assert result["player_tag"] == "valid_user"
    assert result["leagueTier"] == {"name": "Unranked"}
    assert result["builderBaseLeague"] == {
        "id": 44000033,
        "name": "Platinum League II",
    }
    assert result["clan"] == {"tag": "#mock_clan_tag", "role": "coLeader"}
    assert result["num_items"] == 6

    assert user.clantag == "mock_clan_tag"
    assert user.league == 0
    assert user.recruiter_status
    assert user.user_name == "valid_user"


def test_check_player_single_digit_league_tier(monkeypatch) -> None:
    user = API("valid_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "leagueTier": {"name": "Skeleton 1"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "townHallWeaponLevel": 5,
        "expLevel": 100,
        "builderBaseLeague": {
            "id": 44000033,
            "name": "Platinum League II",
        },
        "builderHallLevel": 9,
        "clan": {"tag": "#mock_clan_tag"},
        "role": "coLeader",
        "name": "valid_user",
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    user.check_player()
    assert user.league == 1


def test_check_player_double_digit_league_tier(monkeypatch) -> None:
    user = API("valid_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "leagueTier": {"name": "Titan League 27"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "townHallWeaponLevel": 5,
        "expLevel": 100,
        "builderBaseLeague": {
            "id": 44000033,
            "name": "Platinum League II",
        },
        "builderHallLevel": 9,
        "clan": {"tag": "#mock_clan_tag"},
        "role": "coLeader",
        "name": "valid_user",
    }
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    user.check_player()
    assert user.league == 27


def test_check_player_with_token_verification_fails(monkeypatch) -> None:
    user = API("valid_user", api="invalid-token", headers=MOCK_HEADERS)

    fake_get_response = Mock()
    fake_get_response.json.return_value = {
        "leagueTier": {"name": "Unranked"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "clan": {"tag": "#mock_clan_tag"},
        "role": "leader",
        "name": "valid_user",
    }
    fake_post_response = Mock()
    fake_post_response.json.return_value = {"status": "invalid"}

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        Mock(return_value=fake_get_response),
    )
    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.post",
        Mock(return_value=fake_post_response),
    )

    assert not user.check_player()
    assert user.reason == "API Token is incorrect"


def test_check_player_with_token_verification_succeeds(monkeypatch) -> None:
    user = API("valid_user", api="valid-token", headers=MOCK_HEADERS)

    fake_get_response = Mock()
    fake_get_response.json.return_value = {
        "leagueTier": {"name": "Titan League 27"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "clan": {"tag": "#mock_clan_tag"},
        "role": "leader",
        "name": "valid_user",
    }
    fake_post_response = Mock()
    fake_post_response.json.return_value = {"status": "ok"}

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        Mock(return_value=fake_get_response),
    )
    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.post",
        Mock(return_value=fake_post_response),
    )

    assert user.check_player()
    assert user.token is True
    assert user.user_name == "valid_user"


def test_check_player_request_subset_without_clan_num_items_5(
    monkeypatch,
) -> None:
    user = API("valid_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {
        "leagueTier": {"name": "Unranked"},
        "townHallLevel": 17,
        "builderBaseTrophies": 2000,
        "expLevel": 100,
        "builderBaseLeague": {"id": 44000033, "name": "Platinum League II"},
        "builderHallLevel": 9,
        "name": "valid_user",
    }

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        Mock(return_value=fake_response),
    )

    result = user.check_player([
        "expLevel",
        "leagueTier",
        "builderBaseLeague",
        "builderHallLevel",
        "clan",
    ])

    assert result["player_tag"] == "valid_user"
    assert result["clan"] is None
    assert result["num_items"] == 5


@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"clan": {"tag": "#X"}, "role": "leader"}, True),
        ({"clan": {"tag": "#X"}, "role": "coleader"}, True),
        ({"clan": {"tag": "#X"}, "role": "admin"}, True),
        ({"clan": {"tag": "#X"}, "role": "member"}, False),
        ({"role": "leader", "clan": {}}, False),
    ],
)
def test_recruiting_role_matrix(payload: dict, expected: bool) -> None:
    user = API("valid_user", api=None, headers=MOCK_HEADERS)
    assert user.recruiting(payload) is expected
    
