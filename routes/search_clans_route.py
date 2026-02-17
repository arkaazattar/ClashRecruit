from flask import Blueprint, Flask, request, jsonify, session
from ..api.recruitee_api import Recruitee
from ..config import headers
search_clans_bp = Blueprint("search_clans", __name__)


@search_clans_bp.route("/search_clans", methods=["POST"])
def search_clans():
    filters = request.get_json()
    user = Recruitee(session.get("player_tag"), session.get("player_townhall"), session.get("player_league"), headers)
    clans = user.searchClan(filters, filters.get("after"))
     
    return jsonify(clans)