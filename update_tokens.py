import sys
import os
import logging

import requests
from requests.exceptions import Timeout, RequestException
from dotenv import load_dotenv, set_key

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/update_tokens.log", encoding="utf-8"),
              logging.StreamHandler()],
)
logger = logging.getLogger()

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
    logger.error("Отсутствуют обязательные переменные окружения: %s", ", ".join(missing_vars))
    sys.exit(1)

url = f"https://{AMOCRM_DOMAIN}/oauth2/access_token"

data = {
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "grant_type": "refresh_token",
    "refresh_token": REFRESH_TOKEN,
    "redirect_uri": REDIRECT_URI,
}

try:
    logger.info("Отправка запроса на обновление токенов")
    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()

    tokens = response.json()

    logger.info("Токены успешно обновлены.")
    logger.debug("Access Token: %s", tokens.get("access_token"))
    logger.debug("Refresh Token: %s", tokens.get("refresh_token"))

    set_key(".env", "ACCESS_TOKEN", tokens["access_token"])
    set_key(".env", "REFRESH_TOKEN", tokens["refresh_token"])
    logger.info("Токены сохранены в .env")

except Timeout:
    logger.error("Запрос превысил время ожидания.")
except RequestException as e:
    error_message = e.response.json().get(
        "detail", "Произошла ошибка при выполнении запроса"
    )
    logger.error("Произошла ошибка при выполнении запроса: %s", error_message)
except KeyError as e:
    logger.error("Отсутствуют обязательные переменные окружения: %s", e)
except Exception as e:
    logger.exception("Произошла ошибка: %s", e)