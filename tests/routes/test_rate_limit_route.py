def test_database_count_rate_limit_skips_collection(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    calls = 0

    class DummyCollection:
        def count_documents(self, query):
            nonlocal calls
            calls += 1
            return 12

    monkeypatch.setattr(
        home_route,
        "get_clan_collection",
        lambda: DummyCollection(),
    )

    for _ in range(30):
        response = client.get("/database_count")
        assert response.status_code == 200

    response = client.get("/database_count")

    assert response.status_code == 429
    assert response.headers["Retry-After"]
    assert response.get_json() == {
        "message": "Too many requests. Please try again shortly."
    }
    assert calls == 30


def test_session_state_rate_limit_skips_collection_after_limit(
    client, set_session, monkeypatch
):
    import ClashRecruit.routes.session_state_route as session_state_route

    calls = 0

    class FailIfCalledAPI:
        def __init__(self, *args, **kwargs):
            raise AssertionError("API should not be called by /session-state")

    class DummyCollection:
        def find_one(self, query, projection=None):
            nonlocal calls
            calls += 1
            return None

    set_session(
        player_name="Player",
        player_tag="PLAYER123",
        clan_tag="TESTCLAN",
        player_townhall=13,
        player_townhall_weapon_level=4,
    )
    monkeypatch.setattr(session_state_route, "API", FailIfCalledAPI)
    monkeypatch.setattr(
        session_state_route,
        "get_clan_collection",
        lambda: DummyCollection(),
    )

    for _ in range(20):
        response = client.get("/session-state")
        assert response.status_code == 200

    response = client.get("/session-state")

    assert response.status_code == 429
    assert response.headers["Retry-After"]
    assert calls == 20
