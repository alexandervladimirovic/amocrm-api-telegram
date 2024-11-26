import time
import logging

import schedule

from script import main


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/schedule.log", encoding="utf-8"),
              logging.StreamHandler()],
)
logger = logging.getLogger()

def job():
    """
    Job function for scheduling with schedule library.

    This function is supposed to be called by the schedule library.
    It runs the main function of the script and logs exceptions.
    """
    try:
        logger.info("Запуск задачи расписания")
        main()
        logger.info("Задача выполнена успешно")
    except Exception as e:
        logger.error("Ошибка при выполнении задачи: %s", e)

schedule.every().day.at("10:00").do(job)

logger.info("Скрипт запущен. Ожидание выполнения задач.")

while True:
    schedule.run_pending()
    time.sleep(1)