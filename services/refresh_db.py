"""
Refresh all clan membercount inside of the database.
"""

from datetime import datetime, timedelta, timezone
from json import dumps
from ..api.recruiter_api import Recruiter
from ..config import headers
from .mongo_db_client import clan_collection
from celery import Celery

THRESHOLD = timedelta(minutes=10)
app = Celery("refresh_db", broker="redis://localhost:6379/0") 

@app.task
def task():
    refresh_membercount()

def refresh_membercount() -> None:
    """
    Refresh the membercount of all clans that have not been updated in a certain
    time determined by the threshold. 
    """
    outdated_entries = list(clan_collection.find({
        "last_updated" : { '$lte': datetime.now(timezone.utc) - THRESHOLD},
        # handle test pages
        "expires" : { '$ne' : None}
    }))

    for entry in outdated_entries:
        clan = Recruiter(None, entry.get("clan_tag"), headers)
        clan_collection.update_one({"clan_tag" : clan.clan_tag},
                                   {'$set' :
                                    {"last_updated" : datetime.now(timezone.utc),
                                     "clan_info.member_count" : clan.lookup_clan("member_count")
                                     }})

if __name__ == "__main__":
    refresh_membercount()