"""Refresh stored clan member counts on a periodic background schedule."""

from datetime import datetime, timedelta, timezone

from celery.signals import worker_ready

from ..api.recruiter_api import Recruiter
from ..config import headers
from .celery_app import app
from .mongo_db_client import clan_collection

THRESHOLD = timedelta(minutes=10)


@app.task(name="refresh_membercount_task")
def task():
    """Run the member-count refresh cycle as a Celery task."""
    refresh_membercount()


@worker_ready.connect
def run_refresh_on_worker_start(sender=None, **kwargs):
    """Queue the member-count refresh task when a Celery worker starts.

    Args:
        sender (Any, optional): Celery worker instance that triggered the
            signal.
        **kwargs: Additional Celery signal arguments.
    """
    if sender is not None:
        sender.app.send_task("refresh_membercount_task")


def refresh_membercount() -> None:
    """Refresh member counts for clans with stale data."""
    outdated_entries = list(clan_collection.find({
        "last_updated" : { '$lte': datetime.now(timezone.utc) - THRESHOLD},
    }))

    for entry in outdated_entries:
        clan = Recruiter(entry.get("clan_tag"), headers)
        member_count = clan.lookup_clan("member_count").get("member_count")
        clan_collection.update_one(
                                   {
                                       "clan_tag" : clan.clan_tag,
                                       "source": entry.get("source")
                                   },
                                   {'$set' :
                                    {
                                        "last_updated": datetime.now(
                                            timezone.utc
                                        ),
                                     "clan_info.member_count" : member_count
                                     }})

if __name__ == "__main__":
    refresh_membercount()
