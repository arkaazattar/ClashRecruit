import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import apiKey
from clashrecruit import *
from flask import session
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

uri = f"mongodb+srv://arkaazattar_db_user:{os.getenv('DB_PASSWORD')}@clashrecruit.poawkmg.mongodb.net/?appName=clashrecruit"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
# Send a ping to confirm a successful connection
clan_info_db = client["clan_info_db"]
player_info_db = client["player_info_db"]
clan_collection = clan_info_db["clans"]

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

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
        

@app.route("/recruiter", methods= ['GET', 'POST'])
def recruit():
    user_required_league = 0
    if request.method == 'POST':
        
        user_required_league = int(request.form.get("required_league"))
    
    user = Recruiter(session.get("player_tag"), session.get("clan_tag"))
    user.pull_clan_requirements()
    requirements = user.get_requirements()
    requirements[0] = user_required_league

    data = {
        "requirements": requirements,
        "clan_tag": session.get("clan_tag"),
        "player_tag": session.get("player_tag")
    }
    render_data = data.copy()
    
    existing = clan_collection.find_one({"clan_tag": data["clan_tag"]})
    if not existing:
        clan_collection.insert_one(data)

    else: 
        clan_collection.update_one({"clan_tag" : session.get("clan_tag")}, {'$set' : {"requirements" : requirements}})

    return render_template("recruiter.html", data = render_data)

if __name__ == "__main__":


    app.run(debug=True, port=5000)