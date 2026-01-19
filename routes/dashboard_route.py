from flask import Blueprint, render_template, session

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
        return render_template(
            "dashboard.html",
            username = session.get("player_name"),
            recruit_status = session.get("recruiter_status"))