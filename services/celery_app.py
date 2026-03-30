import os
from datetime import timedelta

from celery import Celery


app = Celery(
    "clash_recruiter",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
)

app.conf.beat_schedule = {
    "refresh_membercount_every_5_minutes": {
        "task": "refresh_membercount_task",
        "schedule": timedelta(minutes=5),
    },
    "discover_imported_clans_daily": {
        "task": "discover_imported_clans_task",
        "schedule": timedelta(days=1),
    },
}

# Import task modules after creating the shared app so they register tasks
# against this Celery instance.
from . import refresh_db  # noqa: E402,F401
from . import import_clash_api_clans  # noqa: E402,F401
