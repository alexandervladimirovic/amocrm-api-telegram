import os

import requests
from dotenv import load_dotenv

load_dotenv()


AROCRM_DOMAIN = os.getenv("AMOCRM_DOMAIN")


url = f"https://{AROCRM_DOMAIN}/oauth2/access_token"

data = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "grant_type": "refresh_token",
    "refresh_token": os.getenv("REFRESH_TOKEN"),
    "redirect_uri": os.getenv("REDIRECT_URI")
}


response = requests.post(url, json=data)


if response.status_code == 200:
    tokens = response.json()
    print("New Access Token:", tokens["access_token"])
    print("New Refresh Token:", tokens["refresh_token"])
else:
    print("Error: ", response.status_code, response.json())