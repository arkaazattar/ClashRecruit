def test_session_state_user_info_returns_empty_for_guest(client, monkeypatch):
    import ClashRecruit.routes.session_state_route as session_state_route

    class _FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError(
                "API should not be called for Guest user-info"
                )

    monkeypatch.setattr(session_state_route, "API", _FailIfCalledAPI)

    response = client.get("/session-state/user-info")

    assert response.status_code == 200
    assert response.get_json() == {}


def test_session_state_user_info_returns_player_stats(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.session_state_route as session_state_route

    class DummyAPI:
        instances = []

        def __init__(self, player_tag, api_token, headers):
            self.player_tag = player_tag
            self.api_token = api_token
            self.headers = headers
            self.requested_fields = None
            DummyAPI.instances.append(self)

        def check_player(self, fields):
            self.requested_fields = fields
            return {
                "player_tag": self.player_tag,
                "expLevel": 120,
                "leagueTier": {"name": "Champion League"},
                "builderBaseLeague": {"name": "Emerald League"},
                "builderHallLevel": 10,
                "clan": {"tag": "#TESTCLAN"},
            }

    set_session(player_tag="PLAYER123")
    monkeypatch.setattr(session_state_route, "API", DummyAPI)

    response = client.get("/session-state/user-info")

    assert response.status_code == 200
    assert response.get_json() == {
        "player_tag": "PLAYER123",
        "expLevel": 120,
        "leagueTier": {"name": "Champion League"},
        "builderBaseLeague": {"name": "Emerald League"},
        "builderHallLevel": 10,
        "clan": {"tag": "#TESTCLAN"},
    }
    assert DummyAPI.instances[0].api_token is None
    assert DummyAPI.instances[0].requested_fields == [
        "expLevel",
        "leagueTier",
        "builderBaseLeague",
        "builderHallLevel",
        "clan",
    ]
