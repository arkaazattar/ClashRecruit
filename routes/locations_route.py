"""Register routes for retrieving stored Clash of Clans locations."""

from flask import Blueprint, jsonify

from ..services.mongo_db_client import get_location_collection

locations_bp = Blueprint("locations", __name__)


@locations_bp.route("/clash_locations", methods=["GET"])
def clash_locations():
    """Return all stored Clash of Clans locations as a JSON array."""
    location_collection = get_location_collection()
    locations = list(location_collection.find({}, {"_id": 0}))

    return jsonify(
        locations
    )

