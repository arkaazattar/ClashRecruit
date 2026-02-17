"""
Refresh all clan membercount inside of the database.
"""

from datetime import datetime, timedelta, timezone
from json import dumps
from ..api.recruiter_api import Recruiter
from ..config import headers
from .mongo_db_client import clan_collection

def refresh_membercount(list_of_clans) -> None:
    """
    Refresh the inputted json list's clans within the database. This function calls 
    the lookup_clan() function within the Recruiter API class. 
    """
