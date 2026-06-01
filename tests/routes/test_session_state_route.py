class DummyClanCollection:
    def __init__(self, listing):
        self.listing = listing
        self.find_one_query = None
        self.find_one_projection = None

    def find_one(self, query, projection):
        self.find_one_query = query
        self.find_one_projection = projection
        return self.listing


def test_session_state_returns_guest_defaults(client, monkeypatch):
    import ClashRecruit.routes.session_state_route as session_state_route

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called for Guest")

    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)

    response = client.get("/session-state")

    assert response.status_code == 200
    assert response.get_json() == {
        "username": "Guest",
        "recruit_status": False,
        "has_active_listing": False,
        "townhall": None,
        "townhallWeaponLevel": None,
    }


def test_session_state_ignores_cached_player_stats_for_guest(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called for Guest")

    set_session(
        player_name="Guest",
        player_townhall=14,
        player_townhall_weapon_level=3,
    )
    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)

    response = client.get("/session-state")

    assert response.status_code == 200
    assert response.get_json()["townhall"] is None
    assert response.get_json()["townhallWeaponLevel"] is None


def test_session_state_returns_logged_in_player_and_active_listing(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    collection = DummyClanCollection(listing={"_id": "listing-id"})
    set_session(
        player_name="test_player",
        player_tag="PLAYER123",
        recruiter_status=True,
        clan_tag="SESSIONCLAN",
        player_townhall=14,
        player_townhall_weapon_level=3,
    )

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called by /session-state")

    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)
    monkeypatch.setattr(
        session_state_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/session-state")

    assert response.status_code == 200
    assert response.get_json() == {
        "username": "test_player",
        "recruit_status": True,
        "has_active_listing": True,
        "townhall": 14,
        "townhallWeaponLevel": 3,
    }
    assert collection.find_one_query["clan_tag"] == "SESSIONCLAN"
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 1}


def test_session_state_returns_logged_in_player_without_active_listing(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    collection = DummyClanCollection(listing=None)
    set_session(
        player_name="test_player",
        player_tag="PLAYER123",
        recruiter_status=True,
        clan_tag="SESSIONCLAN",
        player_townhall=14,
        player_townhall_weapon_level=3,
    )

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called by /session-state")

    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)
    monkeypatch.setattr(
        session_state_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/session-state")

    assert response.status_code == 200
    assert response.get_json() == {
        "username": "test_player",
        "recruit_status": True,
        "has_active_listing": False,
        "townhall": 14,
        "townhallWeaponLevel": 3,
    }
    assert collection.find_one_query["clan_tag"] == "SESSIONCLAN"


def test_session_state_uses_session_clan_tag_without_live_refresh(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    collection = DummyClanCollection(listing={"_id": "listing-id"})
    set_session(
        player_name="test_player",
        player_tag="PLAYER123",
        recruiter_status=True,
        clan_tag="SESSIONCLAN",
        player_townhall=14,
        player_townhall_weapon_level=3,
    )

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called by /session-state")

    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)
    monkeypatch.setattr(
        session_state_route,
        "get_clan_collection",
        lambda: collection,
    )

    response = client.get("/session-state")

    assert response.status_code == 200
    assert response.get_json() == {
        "username": "test_player",
        "recruit_status": True,
        "has_active_listing": True,
        "townhall": 14,
        "townhallWeaponLevel": 3,
    }
    assert collection.find_one_query["clan_tag"] == "SESSIONCLAN"
