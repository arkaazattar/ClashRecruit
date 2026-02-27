from flask import Blueprint, jsonify
from ..services.mongo_db_client import location_collection

locations_bp = Blueprint("locations", __name__)


@locations_bp.route("/clash_locations", methods=["GET"])
def clash_locations():
    locations = list(location_collection.find({}, {"_id": 0}))
    
    return jsonify(
        locations
    )
    
