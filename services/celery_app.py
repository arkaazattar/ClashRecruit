"""Shared Celery app configuration and periodic task scheduling."""

import os
from datetime import timedelta

from celery import Celery

app = Celery(
    "clash_recruiter",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    include=[
        "ClashRecruit.services.import_clash_api_clans",
        "ClashRecruit.services.refresh_db",
    ],
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
