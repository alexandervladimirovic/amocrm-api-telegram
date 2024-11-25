import os

import requests
from requests.exceptions import Timeout, RequestException
from dotenv import load_dotenv, set_key

load_dotenv(override=True)

AMOCRM_DOMAIN = os.getenv("AMOCRM_DOMAIN")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("REFRESH_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI")

required_vars = {
    "AMOCRM_DOMAIN": AMOCRM_DOMAIN,
    "CLIENT_ID": CLIENT_ID,
    "CLIENT_SECRET": CLIENT_SECRET,
    "REFRESH_TOKEN": REFRESH_TOKEN,
    "REDIRECT_URI": REDIRECT_URI,
}

missing_vars = [key for key, value in required_vars.items() if value is not value]

if missing_vars:
    print(f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}")
    exit(1)

url = f"https://{AMOCRM_DOMAIN}/oauth2/access_token"

data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "redirect_uri": REDIRECT_URI,
}

try:
    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()

    tokens = response.json()
    
    print("Токены успешно обновлены:")
    print("Access Token: [скрыто]")
    print("Refresh Token: [скрыто]")

    set_key(".env", "ACCESS_TOKEN", tokens["access_token"])
    set_key(".env", "REFRESH_TOKEN", tokens["refresh_token"])
    print("Токены сохранены в .env")

except Timeout:
    print("Запрос превысил время ожидания")
except RequestException as e:
    error_message = e.response.json().get("detail", "Произошла ошибка при выполнении запроса")
    print(f"Произошла ошибка при выполнении запроса: {error_message}")
except KeyError as e:
    print(f"Ошибка при обработке ответа: отсутствует ключ {e}")
except Exception as e:
    print(f"Произошла неизвестная ошибка: {e}")

   

