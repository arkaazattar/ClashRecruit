def test_database_count_returns_mocked_count(client, monkeypatch):
    import ClashRecruit.routes.home_route as home_route

    class DummyCollection:
        def count_documents(self, query):
            assert query == {}
            return 42

    monkeypatch.setattr(
        home_route, "get_clan_collection", lambda: DummyCollection()
        )

    response = client.get("/database_count")

    assert response.status_code == 200
    assert response.get_json() == {"clan_count": 42}
