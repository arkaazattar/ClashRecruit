from unittest.mock import Mock

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
    fake_response.json.return_value = {"reason" : "notFound"}
    mock_post = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_post,
    )

    assert not invalid_user.check_player()
    assert invalid_user.reason == "Player tag is incorrect"


def test_invalid_ip_address(monkeypatch) -> None:
    user = API("invalid_ip_user", api=None, headers=MOCK_HEADERS)

    fake_response = Mock()
    fake_response.json.return_value = {"reason" : "accessDenied.invalidIp"}
    mock_get = Mock(return_value=fake_response)

    monkeypatch.setattr(
        "ClashRecruit.api.clash_api.requests.get",
        mock_get,
    )

    assert not user.check_player()
    assert user.reason == "Invalid IP"
