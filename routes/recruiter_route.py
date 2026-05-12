"""Register routes for handling recruiter requests."""

from flask import Blueprint, jsonify, request, session

from ..services.recruiter_listing import (
    get_recruiter_listing_page,
    handle_recruiter_listing_action,
)

recruiter_bp = Blueprint("recruiter", __name__)


@recruiter_bp.route("/recruiter", methods=["GET", "POST"])
def recruit():
    """Return recruiter listing data or create, update, and remove listings."""
    if not session.get("recruiter_status"):
        return jsonify({"message": "Forbidden"}), 403

    if request.method == "GET":
        payload, status_code = get_recruiter_listing_page(
            session.get("clan_tag")
        )
        return jsonify(payload), status_code

    data = request.get_json(silent=True) or {}
    payload, status_code = handle_recruiter_listing_action(
        session.get("clan_tag"),
        session.get("player_tag"),
        data,
    )
    return jsonify(payload), status_code
