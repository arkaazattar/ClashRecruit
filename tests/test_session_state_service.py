from ClashRecruit.services.session_state import (
    USER_INFO_FIELDS,
    get_session_state_payload,
    get_user_info_payload,
)


class DummyClanCollection:
    def __init__(self, listing):
        self.listing = listing
        self.find_one_query = None
        self.find_one_projection = None

    def find_one(self, query, projection):
        self.find_one_query = query
        self.find_one_projection = projection
        return self.listing


def test_session_state_payload_ignores_guest_cached_stats():
    collection = DummyClanCollection(listing=None)

    payload = get_session_state_payload(
        username="Guest",
        recruit_status=False,
        clan_tag=None,
        townhall=14,
        townhall_weapon_level=3,
        clan_collection=collection,
    )

    assert payload == {
        "username": "Guest",
        "recruit_status": False,
        "has_active_listing": False,
        "townhall": None,
        "townhallWeaponLevel": None,
    }
    assert collection.find_one_query is None


def test_session_state_payload_checks_active_listing_for_logged_in_player():
    collection = DummyClanCollection(listing={"_id": "listing-id"})

    payload = get_session_state_payload(
        username="test_player",
        recruit_status=True,
        clan_tag="SESSIONCLAN",
        townhall=14,
        townhall_weapon_level=3,
        clan_collection=collection,
    )

    assert payload == {
        "username": "test_player",
        "recruit_status": True,
        "has_active_listing": True,
        "townhall": 14,
        "townhallWeaponLevel": 3,
    }
    assert collection.find_one_query["clan_tag"] == "SESSIONCLAN"
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 1}


def test_user_info_payload_returns_empty_without_player_tag():
    def fail_api_factory(tag):
        raise AssertionError("API should not be called")

    assert get_user_info_payload(None, fail_api_factory) == {}


def test_user_info_payload_returns_selected_player_stats():
    class DummyAPI:
        def __init__(self, player_tag):
            self.player_tag = player_tag
            self.requested_fields = None

        def check_player(self, fields):
            self.requested_fields = fields
            return {"player_tag": self.player_tag, "expLevel": 120}

    instances = []

    def api_factory(player_tag):
        api = DummyAPI(player_tag)
        instances.append(api)
        return api

    assert get_user_info_payload("PLAYER123", api_factory) == {
        "player_tag": "PLAYER123",
        "expLevel": 120,
    }
    assert instances[0].requested_fields == USER_INFO_FIELDS
