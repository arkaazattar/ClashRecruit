from flask import Blueprint, jsonify, session
dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
        return jsonify(username = session.get("player_name"),
            recruit_status = session.get("recruiter_status"))           