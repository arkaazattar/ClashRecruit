from flask import Flask
from flask_cors import CORS
import os
from .config import FLASK_SECRET_KEY
from .api.recruiter_api import Recruiter
from .routes.home_route import home_bp
from .routes.dashboard_route import dashboard_bp
from .routes.recruiter_route import recruiter_bp
from .routes.recruitee_route import recruitee_bp
from .routes.search_clans_route import search_clans_bp

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = FLASK_SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app) 

app.register_blueprint(home_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(recruiter_bp)
app.register_blueprint(recruitee_bp)
app.register_blueprint(search_clans_bp)

if __name__ == "__main__":
    app.run(port=5000)