import os
from datetime import datetime, timedelta

import requests
from telegram import Bot
from dotenv import load_dotenv


load_dotenv(override=True)

AMOCRM_DOMAIN = os.getenv("AMOCRM_DOMAIN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def get_leads():
    """
    Retrieve a list of leads that were closed yesterday.

    Makes a request to the AmoCRM API to fetch leads that were closed yesterday.
    Filters the leads by status and closed date.
    For each lead, adds the status name and responsible user name to the lead dictionary.
    Returns a list of leads with their status names and responsible user names.
    Handles request timeouts and other request-related exceptions.
    """
    url = f"https://{AMOCRM_DOMAIN}/api/v4/leads"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    status_names = get_status_names()
    user_names = get_user_names()

    if not status_names:
        print("Невозможно получить имена статусов")
        return []

    if not user_names:
        print("Невозможно получить имена пользователей")
        return []

    params = {
        "filter[closed_at][from]": (datetime.now() - timedelta(days=1)).strftime(
            "%Y-%m-%d"
        ),
        "filter[closed_at][to]": datetime.now().strftime("%Y-%m-%d"),
        "filter[statuses][0][status]": "142",
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        leads = data["_embedded"]["leads"]

        for lead in leads:
            lead_status_id = str(lead["status_id"])
            lead_responsible_user_id = str(lead["responsible_user_id"])

            lead["status_name"] = status_names.get(lead_status_id, "Неизвестный статус")
            lead["responsible_user_name"] = user_names.get(
                lead_responsible_user_id, "Неизвестный пользватель"
            )

        return leads

    except requests.Timeout:
        print("Запрос превысил время ожидания")
        return []

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        return []


def get_status_names():
    """
    Retrieve the names of all statuses in the AmoCRM pipelines.

    Makes a request to the AmoCRM API to fetch the pipelines and their statuses.
    Returns a dictionary where keys are status IDs and values are status names.

    """
    url = f"https://{AMOCRM_DOMAIN}/api/v4/leads/pipelines"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        statuses = {}

        for pipeline in data["_embedded"]["pipelines"]:
            for status_id, status_data in pipeline["statuses"].items():
                statuses[status_id] = status_data["name"]

        return statuses

    except requests.Timeout:
        print("Запрос превысил время ожидания")
        return {}

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        return {}


def get_user_names():
    """
    Retrieve the names of all users in the AmoCRM account.

    Makes a request to the AmoCRM API to fetch users and their details.
    Returns a dictionary where keys are user IDs (as strings) and values are user names.

    Handles request timeouts and other request-related exceptions.
    """
    url = f"https://{AMOCRM_DOMAIN}/api/v4/users"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        users = {str(user["id"]): user["name"] for user in data["_embedded"]["users"]}
        return users

    except requests.Timeout:
        print("Запрос превысил время ожидания")
        return {}

    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при выполнении запроса: {e}")
        return {}


def group_leads_by_manager(leads):
    """
    Group a list of leads by their responsible user (manager).

    Accepts a list of leads, where each lead is a dictionary with a "responsible_user_id" key.
    Uses the AmoCRM API to fetch the names of all users in the account.
    Returns a dictionary where keys are user names and values are lists of leads for which the user is responsible.

    Handles request timeouts and other request-related exceptions.
    """

    user_names = get_user_names()
    grouped = {}

    for lead in leads:
        manager_id = str(lead["responsible_user_id"])
        manager_name = user_names.get(manager_id, "Неизвестный менеджер")

        if manager_name not in grouped:
            grouped[manager_name] = []
        grouped[manager_name].append(lead)

    return grouped


def send_message_to_telegram(message):
    """
    Sends a message to a specified Telegram chat.

    Uses the Telegram Bot API to send a text message to the chat identified by CHAT_ID.
    """
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)


if __name__ == "__main__":

    leads = get_leads()
    leads_by_manager = group_leads_by_manager(leads)

    # MESSAGE

    message = "Выручка за вчерашний день:\n"

    for manager, manager_leads in leads_by_manager.items():
        total_revenue = sum(lead.get("price", 0) for lead in manager_leads)
        message += f"Менеджер {manager}: {total_revenue} руб.\n"

    # SEND TO TELEGRAM

    send_message_to_telegram(message)
