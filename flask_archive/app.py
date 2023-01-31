import os
import sys

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash
from flask_babel import Babel

import config
import helpers.helpers as h

# Configure application
app = Flask(__name__)
app.config.from_object(config.Config())
Session(app)
db = SQL(config.uri)
mail = Mail(app)
mail.init_app(app)
babel = Babel(app)


@babel.localeselector
def get_locale():
    if "user_id" not in session:
        # If user is not logged in.
        return "en"
    else:
        return db.execute(
            "SELECT language FROM settings WHERE user_id = ?", session["user_id"]
        )[0]["language"]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@h.login_required
def index():
    """Show the user-configured garden"""

    plants, selected_plants = h.prepare_plant_data(db, session["user_id"])

    # Keep only the selected plants in the data to be sent to the client.
    plants = [plant for plant in plants if plant["id"] in selected_plants]

    return render_template("index.html", plants=plants)


@app.route("/planner", methods=["GET", "POST"])
@h.login_required
def planner():
    """Plan the garden by selecting the plants to be grown."""

    if request.method == "POST":

        # Get the plants, selected by the user and format them into a comma separated
        # string, to be stored in the selected_plants database.
        user_selection = ""
        for key in request.form.keys():
            user_selection += key + ","
        user_selection = user_selection[:-1]

        db.execute(
            "UPDATE selected_plants\
                SET selected_plants = ?\
              WHERE user_id = ?",
            user_selection,
            session["user_id"],
        )

        # Flash the message for the user
        flash("Garden successfully updated!")

        # Redirect user to home page
        return redirect("/")

    else:

        plants, selected_plants = h.prepare_plant_data(db, session["user_id"])

        return render_template(
            "planner.html", plants=plants, selected_plants=selected_plants
        )


@app.route("/weekly", methods=["GET", "POST"])
@h.login_required
def weekly():
    """Show the user a weekly summary of work to do in the garden."""

    if request.method == "POST":

        h.send_summary(db, mail, session["user_id"])

        flash("Summary sent to the e-mails, configured in your settings.")

    weekly_todos = h.prepare_weekly_todos(db, session["user_id"])

    # TODO: Pass the weekly todos already with full strings (as per TASK_NAMES dict), in order to avoid hardcoding in html template.
    return render_template("weekly.html", weekly_todos=weekly_todos)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return h.apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return h.apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return h.apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/password_change", methods=["GET", "POST"])
@h.login_required
def password_change():
    """Allow the user to change their password"""

    if request.method == "POST":

        # Ensure username was submitted
        if (
            not request.form.get("password_old")
            or not request.form.get("password_new")
            or not request.form.get("password_confirm")
        ):
            return h.apology("must provide password", 403)

        # Ensure that the old password is correct.
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password_old")
        ):
            return h.apology("old password is not correct", 403)

        # Ensure the password and its confirmation matches
        elif request.form.get("password_new") != request.form.get("password_confirm"):
            return h.apology("passwords do not match", 400)

        # Store the username and hashed password in the database
        db.execute(
            "UPDATE users\
                SET hash = ?\
                WHERE id = ?;",
            generate_password_hash(request.form.get("password_new")),
            session["user_id"],
        )

        return redirect("/")

    else:
        return render_template("password_change.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return h.apology("must provide username", 400)

        # Ensure e-mail was submitted
        if not request.form.get("e-mail"):
            return h.apology("must provide e-mail", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return h.apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return h.apology("passwords do not match", 400)

        # Store the username and hashed password in the database
        try:
            db.execute(
                "INSERT INTO users (username, hash)\
                    VALUES (?, ?);",
                request.form.get("username"),
                generate_password_hash(request.form.get("password")),
            )
        # The username already exists in the database
        except ValueError:
            return h.apology("username already taken", 400)

        user_id = db.execute(
            "SELECT id\
               FROM users\
              WHERE username=?",
            request.form.get("username"),
        )

        # Create an entry for the user in the settings database
        db.execute(
            "INSERT INTO settings (user_id, emails, notifications, language)\
             VALUES (?, ?, NULL, 'en');",
            user_id[0]["id"],
            request.form.get("e-mail"),
        )

        # Create an entry for the user in the selected_plants database
        db.execute(
            "INSERT INTO selected_plants (user_id, selected_plants)\
             VALUES (?, NULL);",
            user_id[0]["id"],
        )

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/settings", methods=["GET", "POST"])
@h.login_required
def settings():
    """Allow the user to change the account settings."""

    if request.method == "POST":

        if not request.form.get("email_1"):
            return h.apology("please provide a default e-mail", 400)

        # Get the notification days, selected by the user and format them into a comma separated
        # string, to be stored in the settings database.
        notifications = ""
        for key in request.form.keys():
            if key[:6] != "notify":
                continue
            else:
                notifications += key[7:] + ","
        notifications = notifications[:-1]

        emails = ""
        for i in range(1, 6):
            if request.form.get(f"email_{i}"):
                emails += request.form.get(f"email_{i}") + ","
        emails = emails[:-1]

        language = request.form.get("language")

        db.execute(
            "UPDATE settings\
                SET notifications = ?, emails = ?, language = ?\
              WHERE user_id = ?",
            notifications,
            emails,
            language,
            session["user_id"],
        )

        # Notification for the user that the settings have been updated.
        flash("Settings successfully updated!")

        # Redirect user to home page
        return redirect("/")

    else:

        # Select all the user settings.
        settings = db.execute(
            "SELECT *\
            FROM settings\
            WHERE user_id = ?",
            session["user_id"],
        )

        # Extract the emails into a list.
        emails = settings[0]["emails"].split(",")

        # Generate a dictionary with a key for each day, True if notification is set, False if not.
        try:
            set_notifications = settings[0]["notifications"].split(",")
        except AttributeError:
            set_notifications = []
        notifications = {}
        for day in config.WEEK_DAYS:
            if day in set_notifications:
                notifications[day] = True
            else:
                notifications[day] = False

        language = settings[0]["language"]

        return render_template(
            "settings.html",
            no_emails=len(emails),
            emails=emails,
            notifications=notifications,
            language=language,
        )
