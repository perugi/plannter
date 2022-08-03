import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function


def prepare_plant_data(db, VALID_MONTH_NAMES):
    """Query the databases to prepare the plant data for display in tables."""

    # Select all the default (user_id 1, created by admin) and user custom plants.
    all_plants = db.execute(
        "SELECT *\
           FROM plants\
          WHERE user_id = 1\
             OR user_id = ?",
        session["user_id"],
    )

    # Prepare the list to send to the client: in order to format the table, we want to
    # send dictionaries with two keys - name and todos, which is a dictionary of the
    # particular monthly todos.
    plants = []
    for row in all_plants:
        plant = {}
        plant["id"] = row["id"]
        plant["name"] = row["name"]
        todos = {k: row[k] for k in VALID_MONTH_NAMES}
        plant["todos"] = todos
        plants.append(plant)

    selected_plants = db.execute(
        "SELECT selected_plants\
            FROM selected_plants\
            WHERE user_id = ?",
        session["user_id"],
    )

    # The selected plants are stored in as a comma separated string, decode into a list.
    if selected_plants[0]["selected_plants"]:
        selected_plants = [
            int(id) for id in selected_plants[0]["selected_plants"].split(",")
        ]

    return plants, selected_plants
