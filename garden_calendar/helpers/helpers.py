import os

# import requests
import urllib.parse
from datetime import date

# from flask_mail import Mail, Message

# from flask import redirect, render_template, request, session
from functools import wraps

from constants import *


# def apology(message, code=400):
#     """Render message as an apology to user."""

#     def escape(s):
#         """
#         Escape special characters.

#         https://github.com/jacebrowning/memegen#special-characters
#         """
#         for old, new in [
#             ("-", "--"),
#             (" ", "-"),
#             ("_", "__"),
#             ("?", "~q"),
#             ("%", "~p"),
#             ("#", "~h"),
#             ("/", "~s"),
#             ('"', "''"),
#         ]:
#             s = s.replace(old, new)
#         return s

#     return render_template("apology.html", top=code, bottom=escape(message)), code


def prepare_plant_data(db, user_id):
    """Query the databases to prepare the plant data for display in tables."""

    # Select all the default (user_id 1, created by admin) and user custom plants.
    all_plants = db.execute(
        "SELECT *\
           FROM plants\
          WHERE user_id = 1\
             OR user_id = ?",
        user_id,
    )

    # Find the language setting for the particular user
    settings = db.execute("SELECT language FROM settings WHERE user_id = ?", user_id)
    language = settings[0]["language"]

    # Prepare the list to send to the client: in order to format the table, we want to
    # send dictionaries with two keys - name and todos, which is a dictionary of the
    # particular monthly todos.
    plants = []
    for row in all_plants:
        plant = {}
        plant["id"] = row["id"]
        plant["name"] = row["name_" + language]
        todos = {k: row[k] for k in VALID_MONTH_NAMES}
        plant["todos"] = todos
        plants.append(plant)

    selected_plants = db.execute(
        "SELECT selected_plants\
            FROM selected_plants\
            WHERE user_id = ?",
        user_id,
    )

    # The selected plants are stored in as a comma separated string, decode into a list.
    if selected_plants[0]["selected_plants"]:
        selected_plants = [
            int(id) for id in selected_plants[0]["selected_plants"].split(",")
        ]

    return plants, selected_plants


# def prepare_weekly_todos(db, user_id):
#     """Prepare a dictionary with the todos for the week. The keys of the dict represent
#     the activity, while the values are the list of plants for that activity."""

#     plants, selected_plants = prepare_plant_data(db, user_id)

#     # Keep only the selected plants in the data to be sent to the client.
#     plants = [plant for plant in plants if plant["id"] in selected_plants]

#     today = date.today()
#     # Find the part of the month we are in.
#     if today.day <= 10:
#         month_period = 1
#     elif today.day <= 20:
#         month_period = 2
#     else:
#         month_period = 3

#     # TODO: Use the dict, defined in the constants to generate the values in this empty dict.
#     weekly_todos = {"S": [], "Pi": [], "Pr": [], "R": [], "P": []}
#     # Filter out the correct todo, based on the part of the month we are in.
#     for plant in plants:
#         if not plant["todos"][f"todo_{today.month}_{month_period}"] == None:
#             weekly_todos[plant["todos"][f"todo_{today.month}_{month_period}"]].append(
#                 plant["name"]
#             )

#     return weekly_todos


# def send_summary(db, mail, user_id):
#     """Get the data and send a weekly summary mail to the e-mails, as defined in the user settings,
#     with the todos and plants, as configured by the user."""
#     today = date.today()

#     weekly_todos = prepare_weekly_todos(db, user_id)

#     username = db.execute(
#         "SELECT username FROM users WHERE id = ?",
#         user_id,
#     )[
#         0
#     ]["username"]

#     # Get the list of recipient e-mails, defined by the user (stored as comma separated string)
#     settings = db.execute("SELECT * FROM settings WHERE user_id = ?", user_id)
#     recipients = settings[0]["emails"].split(",")

#     msg_subject = "Plannter Task Summary for " + today.strftime("%A, %b %-d")

#     msg_body = f"""
#     <p>Hello, {username}!</p>
#     <p>This is a summary of your weekly garden tasks:</p>
#     """

#     for task in weekly_todos:
#         if weekly_todos[task]:
#             msg_body += f"<p><strong>{config.TASK_NAMES[task][settings[0]['language']]}:</strong> "
#             for plant in weekly_todos[task]:
#                 msg_body += f"{plant}, "
#             msg_body = msg_body[:-2] + "</p>"

#     msg_body += """
#     <p>&nbsp;</p>
#     <p>--</p>
#     <p>To configure your garden, visit the Plannter <a href="https://plannter-web.herokuapp.com/planner">Planning</a> page. To modify the notification settings, visit the Plannter <a href="https://plannter-web.herokuapp.com/settings">Settings</a>.</p>
#     """

#     for recipient in recipients:
#         msg = Message(
#             msg_subject,
#             recipients=[recipient],
#             sender=("Plannter Notifications", "plannter.web@gmail.com"),
#         )
#         msg.html = msg_body
#         mail.send(msg)
