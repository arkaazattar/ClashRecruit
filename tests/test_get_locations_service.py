from unittest.mock import Mock

import ClashRecruit.services.get_locations as locations_service


def test_get_locations_returns_items_from_api(monkeypatch):
    fake_response = Mock()
    fake_response.json.return_value = {
        "items": [{"id": 32000007, "name": "International"}]
    }
    fake_get = Mock(return_value=fake_response)
    monkeypatch.setattr(locations_service.requests, "get", fake_get)

    result = locations_service.get_locations({"Authorization": "Bearer token"})

    assert result == [{"id": 32000007, "name": "International"}]
    fake_get.assert_called_once_with(
        "https://api.clashofclans.com/v1/locations",
        headers={"Authorization": "Bearer token"},
    )


def test_update_location_collection_skips_blank_and_existing_locations(
    monkeypatch,
):
    class DummyLocationCollection:
        def __init__(self):
            self.find_queries = []
            self.inserted = []

        def find_one(self, query):
            self.find_queries.append(query)
            if query == {"id": 32000007}:
                return {"id": 32000007, "name": "Existing"}
            return None

        def insert_one(self, location):
            self.inserted.append(location)

    collection = DummyLocationCollection()
    monkeypatch.setattr(
        locations_service,
        "get_location_collection",
        lambda: collection,
    )
    monkeypatch.setattr(
        locations_service,
        "get_locations",
        lambda headers: [
            {"id": 1, "name": ""},
            {"id": 32000007, "name": "Existing"},
            {"id": 32000008, "name": "New"},
        ],
    )

    locations_service.update_location_collection()

    assert collection.find_queries == [
        {"id": 32000007},
        {"id": 32000008},
    ]
    assert collection.inserted == [{"id": 32000008, "name": "New"}]
