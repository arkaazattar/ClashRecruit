def test_clash_locations_returns_locations_without_mongo_ids(
    client,
    monkeypatch,
):
    import ClashRecruit.routes.locations_route as locations_route

    class DummyLocationCollection:
        def __init__(self):
            self.find_query = None
            self.find_projection = None

        def find(self, query, projection):
            self.find_query = query
            self.find_projection = projection
            return [
                {"id": 32000007, "name": "Canada"},
                {"id": 32000006, "name": "United States"},
            ]

    collection = DummyLocationCollection()
    monkeypatch.setattr(
        locations_route,
        "get_location_collection",
        lambda: collection,
    )

    response = client.get("/clash_locations")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 32000007, "name": "Canada"},
        {"id": 32000006, "name": "United States"},
    ]
    assert collection.find_query == {}
    assert collection.find_projection == {"_id": 0}
