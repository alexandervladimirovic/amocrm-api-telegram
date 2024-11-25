import os

import requests
from dotenv import load_dotenv

load_dotenv()


DOMAIN = os.getenv("DOMAIN")


url = f"https://{DOMAIN}.amocrm.ru/oauth2/access_token"

data = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "grant_type": "refresh_token",
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "redirect_uri": os.getenv("REDIRECT_URI")
}


responce = requests.post(url, json=data)

if responce.status_code == 200:
    tokens = responce.json()
    print("New Access Token:", tokens["access_token"])
    print("New Refresh Token:", tokens["refresh_token"])
else:
    print("Error: ", responce.status_code, responce.json())