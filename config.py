import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "Content-Type" : "application/json",
    "Authorization" : os.getenv("APIKEY")
}

DBPASSWORD = os.getenv('DBPASSWORD')
FLASKSECRETKEY = os.getenv("FLASKSECRETKEY")