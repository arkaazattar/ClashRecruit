from datetime import datetime


class DummyDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count


class DummyClanCollection:
    def __init__(self, existing=None, deleted_count=1):
        self.existing = existing
        self.deleted_count = deleted_count
        self.find_one_query = None
        self.inserted_doc = None
        self.update_call = None
        self.delete_query = None

    def find_one(self, query):
        self.find_one_query = query
        return self.existing

    def insert_one(self, doc):
        self.inserted_doc = doc

    def update_one(self, query, update):
        self.update_call = (query, update)

    def delete_one(self, query):
        self.delete_query = query
        return DummyDeleteResult(self.deleted_count)


class DummyRecruiter:
    instances = []

    def __init__(self, clan_tag, headers):
        self.clan_tag = clan_tag
        self.headers = headers
        self.requirements = [1, 2, 3]
        self.pull_called = False
        self.lookup_modes = []
        DummyRecruiter.instances.append(self)

    def pull_clan_requirements(self):
        self.pull_called = True
        return self.requirements

    def lookup_clan(self, mode=None):
        self.lookup_modes.append(mode)
        if mode == "description":
            return {"description": "test_clan_description"}

        return {
            "name": "test_clan",
            "description": "original_description",
            "member_count": 40,
        }


def setup_recruiter_route(monkeypatch, collection):
    import ClashRecruit.routes.recruiter_route as recruiter_route

    DummyRecruiter.instances = []
    monkeypatch.setattr(recruiter_route, "Recruiter", DummyRecruiter)
    monkeypatch.setattr(
        recruiter_route,
        "get_clan_collection",
        lambda: collection,
    )
    monkeypatch.setattr(recruiter_route, "refresh", lambda headers: 17)
    return recruiter_route


def test_recruiter_get_forbidden_without_recruiter_status(client):
    response = client.get("/recruiter")

    assert response.status_code == 403
    assert response.get_json() == {"message": "Forbidden"}


def test_recruiter_get_returns_existing_listing(
    client,
    monkeypatch,
    set_session,
):
    existing = {
        "requirements": [4, 1800, 12],
        "clan_info": {"description": "existing_description"},
        "expires": "existing_expiry",
    }
    collection = DummyClanCollection(existing=existing)
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.get("/recruiter")

    assert response.status_code == 200
    assert response.get_json() == {
        "oldRequiredLeague": 4,
        "oldRequiredBuilderLeague": 1800,
        "oldRequiredTownhall": 12,
        "MAXTOWNHALL": 17,
        "clanDescription": "existing_description",
        "status": "existing_expiry",
    }
    assert collection.find_one_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert DummyRecruiter.instances[0].pull_called is True
    assert DummyRecruiter.instances[0].lookup_modes == []


def test_recruiter_get_returns_default_listing_and_lookup_description(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(existing=None)
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.get("/recruiter")

    assert response.status_code == 200
    assert response.get_json() == {
        "oldRequiredLeague": 1,
        "oldRequiredBuilderLeague": 2,
        "oldRequiredTownhall": 3,
        "MAXTOWNHALL": 17,
        "clanDescription": "test_clan_description",
        "status": None,
    }
    assert collection.find_one_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert DummyRecruiter.instances[0].pull_called is True
    assert DummyRecruiter.instances[0].lookup_modes == ["description"]


def test_recruiter_post_creates_new_listing(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection()
    setup_recruiter_route(monkeypatch, collection)
    set_session(
        recruiter_status=True,
        clan_tag="TEST123",
        player_tag="PLAYER123",
    )

    response = client.post(
        "/recruiter",
        json={
            "status": "new",
            "requiredLeague": 5,
            "requiredBuilderLeague": 2400,
            "requiredTownhall": 13,
            "description": "new_description",
        },
    )
    response_json = response.get_json()

    assert response.status_code == 200
    assert response_json["message"] == "Listing created successfully."
    assert response_json["source"] == "live_listing"
    assert response_json["requirements"] == [5, 2400, 13]
    assert response_json["name"] == "test_clan"
    assert response_json["clan_tag"] == "TEST123"
    assert response_json["player_tag"] == "PLAYER123"
    assert response_json["clan_info"]["description"] == "new_description"
    assert response_json["expires"] == response_json["status"]

    assert collection.inserted_doc["source"] == "live_listing"
    assert collection.inserted_doc["requirements"] == [5, 2400, 13]
    assert collection.inserted_doc["clan_info"]["description"] == (
        "new_description"
    )
    assert isinstance(collection.inserted_doc["last_updated"], datetime)
    assert isinstance(collection.inserted_doc["expires"], datetime)


def test_recruiter_post_updates_listing_and_refreshes_expiry(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post(
        "/recruiter",
        json={
            "status": "update",
            "requiredLeague": 6,
            "requiredBuilderLeague": 2600,
            "requiredTownhall": 14,
            "description": "updated_description",
            "updateExpiry": True,
        },
    )
    update_query, update_doc = collection.update_call
    set_doc = update_doc["$set"]

    assert response.status_code == 200
    assert response.get_json()["message"] == "Listing updated successfully."
    assert update_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert set_doc["source"] == "live_listing"
    assert set_doc["requirements"] == [6, 2600, 14]
    assert set_doc["clan_info.description"] == "updated_description"
    assert isinstance(set_doc["last_updated"], datetime)
    assert isinstance(set_doc["expires"], datetime)


def test_recruiter_post_updates_listing_and_preserves_provided_expiry(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post(
        "/recruiter",
        json={
            "status": "update",
            "requiredLeague": 6,
            "requiredBuilderLeague": 2600,
            "requiredTownhall": 14,
            "description": "updated_description",
            "updateExpiry": False,
            "expiry": "provided_expiry",
        },
    )
    update_query, update_doc = collection.update_call
    set_doc = update_doc["$set"]

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "provided_expiry",
        "message": "Listing updated successfully.",
    }
    assert update_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }
    assert set_doc["source"] == "live_listing"
    assert set_doc["requirements"] == [6, 2600, 14]
    assert set_doc["clan_info.description"] == "updated_description"
    assert "expires" not in set_doc


def test_recruiter_post_removes_listing(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(
        existing={"requirements": [1, 2, 3]},
        deleted_count=1,
    )
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post(
        "/recruiter",
        json={"status": "removeListing"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"message": "Successfully deleted entry."}
    assert collection.delete_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }


def test_recruiter_post_remove_listing_returns_404_when_not_deleted(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(
        existing={"requirements": [1, 2, 3]},
        deleted_count=0,
    )
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post(
        "/recruiter",
        json={"status": "removeListing"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"message": "Failed to delete."}
    assert collection.delete_query == {
        "clan_tag": "TEST123",
        "source": {"$ne": "clash_api_import"},
    }


def test_recruiter_post_returns_400_for_unknown_status(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post("/recruiter", json={"status": "unexpected"})

    assert response.status_code == 400
    assert response.get_json() == {"message": "Invalid listing status."}
    assert collection.inserted_doc is None
    assert collection.update_call is None
    assert collection.delete_query is None


def test_recruiter_post_returns_400_for_missing_json_status(
    client,
    monkeypatch,
    set_session,
):
    collection = DummyClanCollection(existing={"requirements": [1, 2, 3]})
    setup_recruiter_route(monkeypatch, collection)
    set_session(recruiter_status=True, clan_tag="TEST123")

    response = client.post("/recruiter")

    assert response.status_code == 400
    assert response.get_json() == {"message": "Invalid listing status."}
