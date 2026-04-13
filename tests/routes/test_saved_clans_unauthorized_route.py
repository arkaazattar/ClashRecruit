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
