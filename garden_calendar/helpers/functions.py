from datetime import date

from django.core.mail import send_mail

from garden_calendar.models import AddEMail

from .constants import *


def prepare_plant_data(plants, language):
    """Prepare the plant data by generating a list of dictionaries to be passed to
    the template. This means selecting the correct name of the plant to be displayed
    (based on the user settings) and separating the todos from a comma-separated string
    to a dict."""

    # Prepare the list to send to the client: in order to format the table, we want to
    # send dictionaries with two keys - name and todos, which is a dictionary of the
    # particular monthly todos.
    plants_formatted = []
    for row in plants:
        plant = {}
        plant["id"] = row.id
        if language == "en":
            plant["name"] = row.name_en
        elif language == "si":
            plant["name"] = row.name_si
        else:
            raise Exception("User language not suppored")
        plant["todos"] = {
            month: todo
            for (todo, month) in zip(row.todos.split(","), VALID_MONTH_NAMES)
        }
        plants_formatted.append(plant)

    return plants_formatted


def prepare_weekly_todos(plants):
    """Prepare a dictionary with the todos for the week. The keys of the dict represent
    the activity, while the values are the list of plants for that activity."""

    today = date.today()
    # Find the part of the month we are in.
    if today.day <= 10:
        month_period = 1
    elif today.day <= 20:
        month_period = 2
    else:
        month_period = 3

    weekly_todos = {key: [] for key in TASK_NAMES.keys()}

    # Filter out the correct todo, based on the part of the month we are in.
    for plant in plants:
        if not plant["todos"][f"todo_{today.month}_{month_period}"] == "N":
            weekly_todos[plant["todos"][f"todo_{today.month}_{month_period}"]].append(
                plant["name"]
            )

    return weekly_todos


def send_summary(request, weekly_todos):
    """Get the data and send a weekly summary mail to the e-mails, as defined in the user settings,
    with the todos and plants, as configured by the user."""
    today = date.today()

    username = request.user.username

    # Get the list of recipient e-mails, defined by the user (stored as comma separated string)
    recipients = [request.user.email]
    recipients += [
        object.email for object in AddEMail.objects.filter(user=request.user)
    ]

    msg_subject = "Plannter Task Summary for " + today.strftime("%A, %b %-d")

    msg_body = f"""
    <p>Hello, {username}!</p>
    <p>This is a summary of your weekly garden tasks:</p>
    """

    for task in weekly_todos:
        if weekly_todos[task]:
            msg_body += (
                f"<p><strong>{TASK_NAMES[task][request.user.language]}:</strong> "
            )
            for plant in weekly_todos[task]:
                msg_body += f"{plant}, "
            msg_body = msg_body[:-2] + "</p>"

    msg_body += """
    <p>&nbsp;</p>
    <p>--</p>
    <p>To configure your garden, visit the Plannter <a href="#">Planning</a> page. To modify the notification settings, visit the Plannter <a href="https://plannter-web.herokuapp.com/settings">Settings</a>.</p>
    """

    for recipient in recipients:
        send_mail(
            subject=msg_subject,
            message="Test message",
            html_message=msg_body,
            from_email='"Plannter Notifications" <plannter.web@gmail.com>',
            recipient_list=[recipient],
            fail_silently=False,
        )
