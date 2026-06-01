from datetime import datetime, timezone
from unittest.mock import Mock

import ClashRecruit.services.refresh_db as refresh_db


def test_refresh_membercount_updates_stale_entries(monkeypatch):
    frozen_now = datetime(2026, 5, 4, tzinfo=timezone.utc)

    class DummyClanCollection:
        def __init__(self):
            self.find_query = None
            self.update_calls = []

        def find(self, query):
            self.find_query = query
            return [
                {"clan_tag": "TEST123", "source": "live_listing"},
                {"clan_tag": "TEST456", "source": "clash_api_import"},
            ]

        def update_one(self, query, update):
            self.update_calls.append((query, update))

    class DummyRecruiter:
        instances = []

        def __init__(self, clan_tag, headers):
            self.clan_tag = clan_tag
            self.headers = headers
            DummyRecruiter.instances.append(self)

        def lookup_clan(self, mode=None):
            return {"member_count": 40 if self.clan_tag == "TEST123" else 35}

    class FakeDatetime:
        @staticmethod
        def now(tz=None):
            return frozen_now

    clan_collection = DummyClanCollection()
    monkeypatch.setattr(
        refresh_db,
        "get_clan_collection",
        lambda: clan_collection,
    )
    monkeypatch.setattr(refresh_db, "Recruiter", DummyRecruiter)
    monkeypatch.setattr(refresh_db, "datetime", FakeDatetime)

    refresh_db.refresh_membercount()

    assert clan_collection.find_query == {
        "last_updated": {"$lte": frozen_now - refresh_db.THRESHOLD},
        "expires": {"$gt": frozen_now},
    }
    assert [instance.clan_tag for instance in DummyRecruiter.instances] == [
        "TEST123",
        "TEST456",
    ]
    assert clan_collection.update_calls == [
        (
            {"clan_tag": "TEST123", "source": "live_listing"},
            {
                "$set": {
                    "last_updated": frozen_now,
                    "clan_info.member_count": 40,
                }
            },
        ),
        (
            {"clan_tag": "TEST456", "source": "clash_api_import"},
            {
                "$set": {
                    "last_updated": frozen_now,
                    "clan_info.member_count": 35,
                }
            },
        ),
    ]


def test_refresh_task_and_worker_start_delegate(monkeypatch):
    refresh_calls = []
    sender = Mock()

    monkeypatch.setattr(
        refresh_db,
        "refresh_membercount",
        lambda: refresh_calls.append(True),
    )

    refresh_db.task()
    refresh_db.run_refresh_on_worker_start(sender=sender)
    refresh_db.run_refresh_on_worker_start(sender=None)

    assert refresh_calls == [True]
    sender.app.send_task.assert_called_once_with("refresh_membercount_task")
