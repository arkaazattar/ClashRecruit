"""Register routes for handling clan search requests."""

from flask import Blueprint, jsonify, request, session

from ..api.recruitee_api import Recruitee
from ..config import headers

search_clans_bp = Blueprint("search_clans", __name__)


@search_clans_bp.post("/search_clans")
def search_clans():
    """Search clans using provided filters and return matching results."""
    filters = request.get_json() or {}
    user = Recruitee(
        session.get("player_tag"),
        session.get("player_townhall"),
        session.get("player_league"),
        headers,
    )
    clans = user.searchClan(filters, filters.get("after"))

    error = clans.get("error")
    if error:
        if (
            error.get("reason") == "badRequest"
            and error.get("message")
            == "At least one filtering parameter must exist"
        ):
            return jsonify({
                "error": (
                    "Add at least one random clan filter before searching."
                ),
                "reason": error.get("reason"),
                "message": error.get("message"),
            }), 400

        return jsonify({
            "error": error.get("message") or "Failed to search clans.",
            "reason": error.get("reason"),
        }), error.get("status") or 400

    return jsonify(clans)
