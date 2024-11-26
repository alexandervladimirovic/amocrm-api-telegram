import time

import schedule

from script import main

def job():
    """
    Schedule and execute the main function.

    This function is intended to be used with the schedule library to run the
    main function at a specified time each day. The main function retrieves
    and processes leads, then sends a summary message to a Telegram chat.
    """
    main()

schedule.every().day.at("10:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)