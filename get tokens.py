import os

import requests
from dotenv import load_dotenv


load_dotenv()


DOMAIN = os.getenv("DOMAIN")


url = f"https://{DOMAIN}.amocrm.ru/oauth2/access_token"

data = {
    "client_id": os.getenv("CLIENT_ID"),
    "client_secret": os.getenv("CLIENT_SECRET"),
    "grant_type": "authorization_code",
    "code": "def5020059514380f9c280029022ba9c4fa9631540f1de055dbcd9b9722711608d7dfb6c241da77ab96bb93cc1255aa18f6118ea2b8ab4955796d65a47564876f0189bd9008d32a5974f4781feb80a051e48d1eaaf24af41f41df67b373d832ca1e0fa78eeae5df178d6885d3a31764539709dd467701fc15948c9b63a611b930990107b283e5bf4f4e1131cd1aa6936589d2a80baa1b8594ac966f83e5ff0bf037d80c24e96df249f449cc3dfcfb24b03ca598d0ee5e48cf36e8f41905a9c6b492dfb3ef36984055c451e33b1ab0ce98ea2e18c3392b2d7411bd294450734099ba007b328a02850c1f5a4c17d2ee96cf0e25e01b8d6b5d595689dc2071aa3f7cc8dc06af83c3688af5e4fb6132c53f69f1243b60583e52f73dc3632fa5e4cbb2433d27b3e3ca645f5bbe9d8ba2fcd732d214cf42584e28c413acf78690451a7ce092ae96943accb01455c911761499f75371e831d9b084b91af8a2d26a16fdce544282d20ce7b134edb3337447cc5a3def51471e19bb28096c17619b3c2b8aeb7842691b1d35aefe64ba5bec0b219280f91dc306e6367817960deb01af6cc7d5115cdb5716af4e77b55bb177adb6ecc3077520782dfd5228a859e82f04ca60650a2d7c2833691a0b8d295494b00e0fa4ba8e0a3d867a225ff18fff2342c56e48f742f826be7acb892",
    "redirect_uri": os.getenv("REDIRECT_URI")
}


responce = requests.post(url, json=data)


if responce.status_code == 200:
    tokens = responce.json()
    print("Access Token:", tokens["access_token"])
    print("Refresh Token:", tokens["refresh_token"])
else:
    print("Error: ", responce.status_code, responce.json())



