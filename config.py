"""Application configuration and environment-backed settings."""

import os

from dotenv import load_dotenv

load_dotenv()

headers = {
    "Content-Type": "application/json",
    "Authorization": os.getenv("APIKEY"),
}

DBURI = os.getenv("DBURI")
FLASKSECRETKEY = os.getenv("FLASKSECRETKEY")
