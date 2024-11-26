import os
import asyncio
import logging
from datetime import datetime, timedelta

import requests
from telegram import Bot
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/script.log", encoding="utf-8"),
              logging.StreamHandler()],
)
logger = logging.getLogger()


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
    logger.info("Получение списка лидов за вччерашний день")
    url = f"https://{AMOCRM_DOMAIN}/api/v4/leads"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    status_names = get_status_names()
    user_names = get_user_names()

    if not status_names:
        logger.info("Невозможно получить имена статусов")
        return []

    if not user_names:
        logger.info("Невозможно получить имена менеджеров")
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
        logger.info("Успешно получено %d лидов.", len(leads))
        return leads

    except requests.Timeout:
        logger.error("Запрос к API превысил время ожидания")
        return []

    except requests.exceptions.RequestException as e:
        logger.error("Ошибка при запросе к API: %s", e)
        return []


def get_status_names():
    """
    Retrieve the names of all statuses in the AMOCRM pipelines.

    Makes a request to the AMOCRM API to fetch the pipelines and their statuses.
    Returns a dictionary where keys are status IDs and values are status names.
    """
    logger.info("Получение имен статусов.")
    url = f"https://{AMOCRM_DOMAIN}/api/v4/leads/pipelines"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "_embedded" not in data or "pipelines" not in data["_embedded"]:
            logger.info("Ответ API не содержит данных о конвейерах")
            return {}

        statuses = {}

        for pipeline in data["_embedded"]["pipelines"]:
            if "_embedded" in pipeline and "statuses" in pipeline["_embedded"]:
                for status in pipeline["_embedded"]["statuses"]:
                    statuses[status["id"]] = status["name"]
            else:
                logger.info(
                    f"В конвейере {pipeline.get('name', 'Без имени')} нет статусов %s"
                )
                # print(json.dumps(data, indent=4, ensure_ascii=False))
        logger.info("Успешно получены статусы")
        return statuses

    except requests.Timeout:
        logger.error("Запрос на получение статусов превысил время ожидания")
        return {}

    except requests.exceptions.RequestException as e:
        logger.error("Ошибка при запросе статусов: %s", e)
        return {}


def get_user_names():
    """
    Retrieve the names of all users in the AmoCRM account.

    Makes a request to the AmoCRM API to fetch users and their details.
    Returns a dictionary where keys are user IDs (as strings) and values are user names.

    Handles request timeouts and other request-related exceptions.
    """
    logger.info("Получение имен пользователей")
    url = f"https://{AMOCRM_DOMAIN}/api/v4/users"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        users = {str(user["id"]): user["name"] for user in data["_embedded"]["users"]}
        logger.info("Успешно получены пользователи")
        return users

    except requests.Timeout:
        logger.error("Запрос на получение пользователей превысил время ожидания")
        return {}

    except requests.exceptions.RequestException as e:
        logger.error("Произошла ошибка при выполнении запроса %s", e)
        return {}


def group_leads_by_manager(leads):
    """
    Group a list of leads by their responsible user (manager).

    Accepts a list of leads, where each lead is a dictionary with a "responsible_user_id" key.
    Uses the AmoCRM API to fetch the names of all users in the account.
    Returns a dictionary where keys are user names and values are lists of leads for which the user is responsible.

    Handles request timeouts and other request-related exceptions.
    """
    logger.info("Группировка лидов по менеджерам")
    user_names = get_user_names()
    grouped = {}

    for lead in leads:
        manager_id = str(lead["responsible_user_id"])
        manager_name = user_names.get(manager_id, "Неизвестный менеджер")

        if manager_name not in grouped:
            grouped[manager_name] = []
        grouped[manager_name].append(lead)
    logger.info("Лиды успешно сгруппированы")
    return grouped


async def send_message_to_telegram_async(message):
    """
    Send an asynchronous message to a Telegram chat.

    This function sends a message to a predefined Telegram chat using the
    Telegram Bot API. The message is sent asynchronously.
    """
    logger.info("Отправка сообщения в Telegram")
    bot = Bot(token=TELEGRAM_TOKEN)
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        logger.info("Сообщение успешно отправлено в Telegram")
    except Exception as e:
        logger.error("Ошибка при отправке сообщения в Telegram: %s", e)


async def main():
    """
    Main entry point of the script.

    Retrieves all leads from the AmoCRM API, groups them by their responsible user (manager),
    calculates the total revenue for each manager, and sends a message to a Telegram chat
    with the results.
    """
    logger.info("Запуск скрипта")
    leads = get_leads()
    leads_by_manager = group_leads_by_manager(leads)

    message = "Выручка за вчерашний день:\n"

    for manager, manager_leads in leads_by_manager.items():
        total_revenue = sum(lead.get("price", 0) for lead in manager_leads)
        message += f"Менеджер: {manager}: {total_revenue} руб.\n"

    await send_message_to_telegram_async(message)


if __name__ == "__main__":
    asyncio.run(main())
