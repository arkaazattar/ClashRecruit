def test_saved_clans_get_unauthorized_returns_401(client, monkeypatch):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        pass

    def get_dummy_user_collection():
        return DummyUserCollection()

    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        get_dummy_user_collection,
    )

    response = client.get("/saved-clans")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}


def test_saved_clans_post_unauthorized_returns_401(client, monkeypatch):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        pass

    def get_dummy_user_collection():
        return DummyUserCollection()

    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        get_dummy_user_collection,
    )

    response = client.post("/saved-clans/ABC123")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}


def test_saved_clans_delete_unauthorized_returns_401(client, monkeypatch):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    class DummyUserCollection:
        pass

    def get_dummy_user_collection():
        return DummyUserCollection()

    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        get_dummy_user_collection,
    )

    response = client.delete("/saved-clans/ABC123")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}


def test_saved_clans_get_malformed_session_player_tag_returns_401(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    def fail_get_user_collection():
        raise AssertionError("user collection should not be used")

    set_session(player_tag="bad-tag!")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        fail_get_user_collection,
    )

    response = client.get("/saved-clans")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}


def test_saved_clans_post_malformed_session_player_tag_returns_401(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    def fail_get_user_collection():
        raise AssertionError("user collection should not be used")

    set_session(player_tag="bad-tag!")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        fail_get_user_collection,
    )

    response = client.post("/saved-clans/ABC123")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}


def test_saved_clans_delete_malformed_session_player_tag_returns_401(
    client,
    monkeypatch,
    set_session,
):
    import ClashRecruit.routes.saved_clans_route as saved_clans_route

    def fail_get_user_collection():
        raise AssertionError("user collection should not be used")

    set_session(player_tag="bad-tag!")
    monkeypatch.setattr(
        saved_clans_route,
        "get_user_collection",
        fail_get_user_collection,
    )

    response = client.delete("/saved-clans/ABC123")

    assert response.status_code == 401
    assert response.get_json() == {"message": "Unauthorized"}
