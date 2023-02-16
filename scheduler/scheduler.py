from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events
from django.utils import timezone
from django_apscheduler.models import DjangoJobExecution
from django.core.exceptions import ObjectDoesNotExist

from garden_calendar.helpers.functions import (
    prepare_plant_data,
    prepare_weekly_todos,
    send_summary,
)
from garden_calendar.helpers.constants import (
    WEEK_DAYS,
    MAIL_NOTIFICATIONS_HOUR,
    MAIL_NOTIFICATIONS_MINUTE,
)
from garden_calendar.models import Plant, User, AddEMail

from datetime import date


def send_mail_notifications():
    users = User.objects.exclude(id=1)
    today = date.today()

    for user in users:
        # Check if the user has a notification set for today.
        if WEEK_DAYS[today.weekday()] in user.notifications:
            try:
                plants = user.selected_plants.all()
                plants = prepare_plant_data(plants, user.language)
            except ObjectDoesNotExist:
                # User has not selected any plants yet.
                plants = []

            weekly_todos = prepare_weekly_todos(plants)

            send_summary(user, weekly_todos)


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")
    scheduler.add_job(
        send_mail_notifications,
        "cron",
        hour=MAIL_NOTIFICATIONS_HOUR,
        minute=MAIL_NOTIFICATIONS_MINUTE,
        timezone="Europe/Ljubljana",
        id="mail_notification",
        jobstore="default",
        replace_existing=True,
    )
    register_events(scheduler)
    scheduler.start()
