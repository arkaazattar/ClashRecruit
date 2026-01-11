import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import apiKey
from clashrecruit import *
from flask import session
from dotenv import load_dotenv


load_dotenv()

template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "templates"))
app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["TEMPLATES_AUTO_RELOAD"] = True
CORS(app) 

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/verify-user", methods=['POST'])

def verify_user():

    data = request.get_json()

    received_tag = data.get('playerTag')
    received_token = data.get('apiToken')
    session["player_tag"] = received_tag
    
    user = API(received_tag, received_token)
    check_player_team = user.check_player()
    session["recruiter_status"] = user.recruiter_status
    print(f"This should be the recruiter status : {user.recruiter_status}")

    if check_player_team == True:
        status = True
        reason = "Valid User"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag
    else:
        status = False
        reason = f"{user.reason}"
        name = user.user_name
        session["player_name"] = name
        clan_tag = user.clantag
        session["clan_tag"] = clan_tag

    return jsonify({
        "message": status, 
        "receivedPlayerTag": reason,
        "recruit_status" : session.get("recruiter_status"),
        "player_name" : name,
        "clan_tag" : clan_tag
    })

@app.route("/dashboard")
def dashboard():
        return render_template(
            "dashboard.html",
            username = session.get("player_name"),
            recruit_status = session.get("recruiter_status"))
        

@app.route("/recruiter")
def recruit():
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"))
    user.pull_clan_requirements()
    requirements = user.get_requirements()

    data = {
        "requirements":  user.get_requirements(),
        "clan_tag": session.get("clan_tag"),
        "player_tag": session.get("player_tag")
    }
    return render_template("recruiter.html", data = data)


if __name__ == "__main__":
    app.run(debug=True, port=5000)