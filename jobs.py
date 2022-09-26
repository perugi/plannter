from cs50 import SQL
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date

import helpers.helpers as h
import config
from app import db, mail

scheduler = BlockingScheduler()


@scheduler.scheduled_job(
    "cron",
    day_of_week="*",
    hour=config.MAIL_NOTIFICATIONS_HOUR,
)
def mail_notifications():

    with scheduler.app.app_context():

        settings = db.execute("SELECT * FROM settings")
        today = date.today()

        for user_settings in settings:
            if user_settings["notifications"]:
                # Check if the user has a notification set for today.
                if config.WEEK_DAYS[today.weekday()] in user_settings["notifications"]:
                    h.send_summary(db, mail, user_settings["user_id"])
