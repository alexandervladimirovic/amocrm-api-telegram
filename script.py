import os
from datetime import datetime, timedelta

import requests
from telegram import Bot
from dotenv import load_dotenv


load_dotenv()

AROCRM_DOMAIN = os.getenv("AMOCRM_DOMAIN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def get_leads():

    """
    Get a list of leads that were closed yesterday, with the "converted to deal" status.

    The AmoCRM API is queried for leads that were closed between yesterday and today, with the status "converted to deal".
    The result is a list of leads, where each lead is represented as a dict.
    """

    url = f"https://{AROCRM_DOMAIN}/api/v4/leads"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    params = {
        "filter[closed_at][from]": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
        "filter[closed_at][to]": datetime.now().strftime("%Y-%m-%d"),
        "filter[statuses][0][status]": "142"
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    return data["_embedded"]["leads"]


def group_leads_by_manager(leads):
    """
    Group a list of leads by their responsible user (manager).
    
    Takes a list of leads, and returns a dict where the keys are the IDs of the responsible users, 
    and the values are the total revenue for all leads assigned to that user.
    """

    leads_by_manager = {}
    for lead in leads:
        manager_id = lead["responsible_user_id"]
        revenue = lead["price"]
        leads_by_manager[manager_id] = leads_by_manager.get(manager_id, 0) + revenue
    
    return leads_by_manager


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

    for manager, revenue in leads_by_manager.items():
        message += f"Менеджер {manager}: {revenue} руб.\n"

    # SEND TO TELEGRAM

    send_message_to_telegram(message)
   