import os

import requests
from dotenv import load_dotenv, set_key

load_dotenv(override=True)


def get_tokens():
    """
    Retrieve an access token for the AmoCRM API.

    Makes a request to the AmoCRM API to fetch an access token.
    Returns a dictionary containing the access token and refresh token.
    Handles request timeouts and other request-related exceptions.
    """

    url = f"https://{os.getenv('AMOCRM_DOMAIN')}/oauth2/access_token"

    data = {
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "code": os.getenv("CODE"),
        "redirect_uri": os.getenv("REDIRECT_URI"),
    }

    try:
        response = requests.post(url, json=data, timeout=10)
        response.raise_for_status()

        tokens = response.json()
        print("Access Token:", tokens.get("access_token"))
        print("Refresh Token:", tokens.get("refresh_token"))

        return tokens

    except requests.exceptions.Timeout:
        print("Ошибка: Запрос превысил время ожидания")

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        if response := e.response:
            print(
                "Детали ошибки:",
                response.json().get("detail", "Не удалось получить детали ошибки"),
            )

    return None


def save_tokens(tokens):
    """
    Saves the given tokens to the .env file.

    The .env file is updated with the new access_token and refresh_token values.
    """
    dotenv_path = ".env"

    set_key(dotenv_path, "ACCESS_TOKEN", tokens["access_token"])
    set_key(dotenv_path, "REFRESH_TOKEN", tokens["refresh_token"])

    print("Токены сохранены в .env")


if __name__ == "__main__":
    required_env_vars = [
        "AMOCRM_DOMAIN",
        "CLIENT_ID",
        "CLIENT_SECRET",
        "CODE",
        "REDIRECT_URI",
    ]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(
            f"Отсутствуют обязательные переменные окружения: {', '.join(missing_vars)}"
        )

    tokens = get_tokens()

    if tokens:
        save_tokens(tokens)
