"""
Refresh all clan membercount inside of the database.
"""

from datetime import datetime, timedelta, timezone
from ..api.recruiter_api import Recruiter
from ..config import headers
from .mongo_db_client import clan_collection
from celery.signals import worker_ready
from .celery_app import app

THRESHOLD = timedelta(minutes=10)

@app.task(name="refresh_membercount_task")
def task():
    refresh_membercount()


@worker_ready.connect
def run_refresh_on_worker_start(sender=None, **kwargs):
    if sender is not None:
        sender.app.send_task("refresh_membercount_task")

def refresh_membercount() -> None:
    """
    Refresh the membercount of all clans that have not been updated in a certain
    time determined by the threshold. 
    """
    outdated_entries = list(clan_collection.find({
        "last_updated" : { '$lte': datetime.now(timezone.utc) - THRESHOLD},
    }))

    for entry in outdated_entries:
        clan = Recruiter(None, entry.get("clan_tag"), headers)
        member_count = clan.lookup_clan("member_count").get("member_count")
        clan_collection.update_one(
                                   {
                                       "clan_tag" : clan.clan_tag,
                                       "source": entry.get("source")
                                   },
                                   {'$set' :
                                    {"last_updated" : datetime.now(timezone.utc),
                                     "clan_info.member_count" : member_count
                                     }})
    
    #testing
    print(len(outdated_entries))

if __name__ == "__main__":
    refresh_membercount()
