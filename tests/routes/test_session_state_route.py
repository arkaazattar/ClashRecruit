class DummyAPI:
    instances = []

    def __init__(self, player_tag, api_token, headers):
        self.player_tag = player_tag
        self.api_token = api_token
        self.headers = headers
        self.townhall = 14
        self.townhallWeaponLevel = 3
        self.clantag = "LIVECLAN"
        self.check_called = False
        DummyAPI.instances.append(self)

    def check_player(self):
        self.check_called = True
        return True


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


def test_session_state_returns_logged_in_player_and_active_listing(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    collection = DummyClanCollection(listing={"_id": "listing-id"})
    DummyAPI.instances = []
    set_session(
        player_name="test_player",
        player_tag="PLAYER123",
        recruiter_status=True,
        clan_tag="SESSIONCLAN",
    )
    monkeypatch.setattr(session_state_route, "API", DummyAPI)
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
    assert DummyAPI.instances[0].player_tag == "PLAYER123"
    assert DummyAPI.instances[0].api_token is None
    assert DummyAPI.instances[0].check_called is True
    assert collection.find_one_query["clan_tag"] == "LIVECLAN"
    assert "$gt" in collection.find_one_query["expires"]
    assert collection.find_one_projection == {"_id": 1}
