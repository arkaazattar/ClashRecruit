"""Flask application entrypoint and blueprint registration for ClashRecruit."""

import os

from flask import Flask
from flask_cors import CORS

from .config import FLASKSECRETKEY
from .routes.home_route import home_bp
from .routes.imported_clans_route import imported_clans_bp
from .routes.locations_route import locations_bp
from .routes.recruitee_route import recruitee_bp
from .routes.recruiter_route import recruiter_bp
from .routes.saved_clans_route import saved_clans_bp
from .routes.search_clans_route import search_clans_bp
from .routes.session_state_route import session_state_bp
from .services.clash_api_preflight import run_clash_api_preflight
from .services.mongo_db_client import initialize_mongo

app = Flask(__name__)
app.secret_key = FLASKSECRETKEY

CORS(app, supports_credentials=True, origins=["http://localhost:3000"])

app.register_blueprint(home_bp)
app.register_blueprint(session_state_bp)
app.register_blueprint(recruiter_bp)
app.register_blueprint(recruitee_bp)
app.register_blueprint(imported_clans_bp)
app.register_blueprint(search_clans_bp)
app.register_blueprint(locations_bp)
app.register_blueprint(saved_clans_bp)


def run_startup_tasks_from_env() -> None:
    """Run optional startup tasks gated by environment flags."""
    if os.getenv("CLASH_DEV_PREFLIGHT", "False").lower() == "true":
        run_clash_api_preflight()
    if os.getenv("CLASH_INIT_DB_ON_START", "False").lower() == "true":
        initialize_mongo()


run_startup_tasks_from_env()


if __name__ == "__main__":
    app.run(port=5000)
