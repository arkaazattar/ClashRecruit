from datetime import datetime, timedelta, timezone

import requests
from flask import Blueprint, jsonify

from ..config import headers

locations_bp = Blueprint("locations", __name__)

_cache = {
    "data": [],
    "expires_at": datetime.min.replace(tzinfo=timezone.utc),
}


@locations_bp.route("/clash_locations", methods=["GET"])
def clash_locations():
    now = datetime.now(timezone.utc)
    if _cache["data"] and now < _cache["expires_at"]:
        return jsonify(_cache["data"])

    try:
        response = requests.get(
            "https://api.clashofclans.com/v1/locations",
            headers=headers,
            params={"limit": 500},
            timeout=10,
        )
        response.raise_for_status()
        items = response.json().get("items", [])
        locations = [
            {"id": item.get("id"), "name": item.get("name")}
            for item in items
            if item.get("id") is not None and item.get("name")
        ]
        locations.sort(key=lambda item: item["name"].lower())
        _cache["data"] = locations
        _cache["expires_at"] = now + timedelta(hours=12)
        return jsonify(locations)
    except requests.RequestException:
        if _cache["data"]:
            return jsonify(_cache["data"])
        return jsonify({"error": "Unable to fetch Clash locations"}), 502
