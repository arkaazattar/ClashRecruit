import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Content-Type" : "application/json",
    "Authorization" : os.getenv("APIKEY")
}

DB_PASSWORD = os.getenv('DB_PASSWORD')
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY")