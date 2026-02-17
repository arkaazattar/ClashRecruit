from datetime import datetime, timezone
from flask import Blueprint, jsonify, session
from ..services.mongo_db_client import clan_collection

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
        username = session.get("player_name", "Guest")
        recruit_status = bool(session.get("recruiter_status"))
        has_active_listing = False

        if username != "Guest" and recruit_status:
            clan_tag = session.get("clan_tag")
            player_tag = session.get("player_tag")
            now = datetime.now(timezone.utc)
            listing = clan_collection.find_one(
                {
                    "clan_tag": clan_tag,
                    "player_tag": player_tag,
                    "expires": {"$gt": now}
                },
                {"_id": 1}
            )
            has_active_listing = listing is not None

        return jsonify(
            username=username,
            recruit_status=recruit_status,
            has_active_listing=has_active_listing
        )
