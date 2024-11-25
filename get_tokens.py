import os

import requests
from dotenv import load_dotenv

load_dotenv()


AROCRM_DOMAIN = os.getenv("AMOCRM_DOMAIN")


url = f"https://{AROCRM_DOMAIN}/oauth2/access_token"

data = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "grant_type": "authorization_code",
    "code": os.getenv("CODE"),
    "redirect_uri": os.getenv("REDIRECT_URI")
}


response = requests.post(url, json=data)


if response.status_code == 200:
    tokens = response.json()
    print("Access Token:", tokens["access_token"])
    print("Refresh Token:", tokens["refresh_token"])
else:
    print("Error: ", response.status_code, response.json())



