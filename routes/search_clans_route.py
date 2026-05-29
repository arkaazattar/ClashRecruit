"""Register routes for handling clan search requests."""

from flask import Blueprint, jsonify, request, session

from ..api.recruitee_api import Recruitee
from ..config import headers
from .rate_limit import rate_limit
from .validation import RequestValidationError, get_json_object

search_clans_bp = Blueprint("search_clans", __name__)


@search_clans_bp.post("/search_clans")
@rate_limit("search_clans", limit=10, window_seconds=60)
def search_clans():
    """Search clans using provided filters and return matching results."""
    try:
        filters = _validate_search_filters(get_json_object(request))
    except RequestValidationError as exc:
        return jsonify({"error": exc.message}), 400

    user = Recruitee(
        session.get("player_tag"),
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
            return jsonify(
                {
                    "error": (
                        "Add at least one random clan filter before searching."
                    ),
                    "reason": error.get("reason"),
                    "message": error.get("message"),
                }
            ), 400

        return jsonify(
            {
                "error": error.get("message") or "Failed to search clans.",
                "reason": error.get("reason"),
            }
        ), error.get("status") or 400

    return jsonify(clans)


def _validate_search_filters(filters):
    """Return a shallow-normalized Clash clan search filter dict."""
    normalized = {}
    for key, value in filters.items():
        if value is None:
            continue
        if isinstance(value, bool) or not isinstance(value, (str, int)):
            raise RequestValidationError(
                f"{key} must be a string or integer."
            )
        if isinstance(value, str):
            value = value.strip()
            if not value:
                continue
        normalized[key] = value
    return normalized
