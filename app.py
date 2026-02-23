from flask import Flask
from flask_cors import CORS
import os
from .config import FLASKSECRETKEY
from .routes.home_route import home_bp
from .routes.dashboard_route import dashboard_bp
from .routes.recruiter_route import recruiter_bp
from .routes.recruitee_route import recruitee_bp
from .routes.search_clans_route import search_clans_bp
from .routes.locations_route import locations_bp

app = Flask(__name__)
app.secret_key = FLASKSECRETKEY
app.config["TEMPLATES_AUTO_RELOAD"] = True

CORS(
    app,
    supports_credentials=True,
    origins=["http://localhost:3000"]
)

app.register_blueprint(home_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(recruiter_bp)
app.register_blueprint(recruitee_bp)
app.register_blueprint(search_clans_bp)
app.register_blueprint(locations_bp)

if __name__ == "__main__":
    app.run(port=5000)
