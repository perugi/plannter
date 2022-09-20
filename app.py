import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date
from flask_apscheduler import APScheduler

from helpers.helpers import apology, login_required, prepare_plant_data

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the app to use the Heroku Postgres database.
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

# Configure the app for sending mail using google mail.
mail = Mail(app)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail.init_app(app)

# Configure the app to use the scheduler and initialize it
scheduler = APScheduler
scheduler.api_enabled = True
scheduler.init_app(app)
scheduler.start()

VALID_MONTH_NAMES = []
for i in range(1, 13):
    for j in range(1, 4):
        VALID_MONTH_NAMES.append(f"todo_{i}_{j}")

WEEK_DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show the user-configured garden"""

    plants, selected_plants = prepare_plant_data(db, VALID_MONTH_NAMES)

    # Keep only the selected plants in the data to be sent to the client.
    plants = [plant for plant in plants if plant["id"] in selected_plants]

    return render_template("index.html", plants=plants)


@app.route("/planner", methods=["GET", "POST"])
@login_required
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

        plants, selected_plants = prepare_plant_data(db, VALID_MONTH_NAMES)

        return render_template(
            "planner.html", plants=plants, selected_plants=selected_plants
        )


@app.route("/weekly")
@login_required
def weekly():
    """Show the user a weekly summary of work to do in the garden."""

    plants, selected_plants = prepare_plant_data(db, VALID_MONTH_NAMES)

    # Keep only the selected plants in the data to be sent to the client.
    plants = [plant for plant in plants if plant["id"] in selected_plants]

    today = date.today()
    # Find the part of the month we are in.
    if today.day <= 10:
        month_period = 1
    elif today.day <= 20:
        month_period = 2
    else:
        month_period = 3

    weekly_todos = {"S": [], "Pi": [], "Pr": [], "R": [], "P": []}
    # Filter out the correct todo, based on the part of the month we are in.
    for plant in plants:
        if not plant["todos"][f"todo_{today.month}_{month_period}"] == None:
            weekly_todos[plant["todos"][f"todo_{today.month}_{month_period}"]].append(
                plant["name"]
            )

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
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

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
@login_required
def password_change():
    """Allow the user to change their password"""

    if request.method == "POST":

        # Ensure username was submitted
        if (
            not request.form.get("password_old")
            or not request.form.get("password_new")
            or not request.form.get("password_confirm")
        ):
            return apology("must provide password", 403)

        # Ensure that the old password is correct.
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password_old")
        ):
            return apology("old password is not correct", 403)

        # Ensure the password and its confirmation matches
        elif request.form.get("password_new") != request.form.get("password_confirm"):
            return apology("passwords do not match", 400)

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
            return apology("must provide username", 400)

        # Ensure e-mail was submitted
        if not request.form.get("e-mail"):
            return apology("must provide e-mail", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

        # Store the username and hashed password in the database
        try:
            db.execute(
                "INSERT INTO users (username, mail, hash)\
                    VALUES (?, ?, ?);",
                request.form.get("username"),
                request.form.get("e-mail"),
                generate_password_hash(request.form.get("password")),
            )
        # The username already exists in the database
        except ValueError:
            return apology("username already taken", 400)

        user_id = db.execute(
            "SELECT id\
               FROM users\
              WHERE username=?",
            request.form.get("username"),
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
@login_required
def settings():
    """Allow the user to change the account settings."""

    if request.method == "POST":

        if not request.form.get("email_1"):
            return apology("please provide a default e-mail", 400)

        # Get the notification days, selected by the user and format them into a comma separated
        # string, to be stored in the settings database.
        notifications = ""
        for key in request.form.keys():
            if key[:6] != "notify":
                continue
            else:
                notifications += key[7:] + ","
        notifications = notifications[:-1]

        db.execute(
            "UPDATE settings\
                SET notifications = ?, email_1 = ?, email_2 = ?, email_3 = ?, email_4 = ?, email_5 = ?\
              WHERE user_id = ?",
            notifications,
            request.form.get("email_1"),
            request.form.get("email_2"),
            request.form.get("email_3"),
            request.form.get("email_4"),
            request.form.get("email_5"),
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

        # Extract the emails into a dictionary.
        emails = {}
        for column in settings[0]:
            if column[:5] == "email" and settings[0][column]:
                emails[column] = settings[0][column]

        # Generate a dictionary with a key for each day, True if notification is set, False if not.
        set_notifications = settings[0]["notifications"].split(",")
        notifications = {}
        for day in WEEK_DAYS:
            if day in set_notifications:
                notifications[day] = True
            else:
                notifications[day] = False

        # TODO remove this
        msg = Message(
            "Hello from the other side!",
            recipients=["dominik.perusko@gmail.com"],
            sender="plannter.web@gmail.com",
        )
        msg.body = "This is a test mail, sent from Flask."
        mail.send(msg)

        return render_template(
            "settings.html",
            no_emails=len(emails),
            emails=emails,
            notifications=notifications,
        )
