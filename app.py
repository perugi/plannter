import os
import sys

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers.helpers import apology, login_required, prepare_plant_data

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure the app to use the local sqlite database.
# db = SQL("sqlite:///plannter.db")

# Configure the app to use the Heroku Postgres database.
uri = os.getenv("DATABASE_URL")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://")
db = SQL(uri)

VALID_MONTH_NAMES = []
for i in range(1, 13):
    for j in range(1, 4):
        VALID_MONTH_NAMES.append(f"todo_{i}_{j}")


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

    VALID_MONTH_NAMES = []
    for i in range(1, 13):
        for j in range(1, 4):
            VALID_MONTH_NAMES.append(f"todo_{i}_{j}")

    # Select all the default (user_id 1, created by admin) and user custom plants.
    all_plants = db.execute(
        "SELECT *\
           FROM plants\
          WHERE user_id = 1\
             OR user_id = ?",
        session["user_id"],
    )

    selected_plants = db.execute(
        "SELECT selected_plants\
           FROM selected_plants\
          WHERE user_id = ?",
        session["user_id"],
    )

    # Prepare the list to send to the client: in order to format the table, we want to
    # send dictionaries with two keys - name and todos, which is a dictionary of the
    # particular monthly todos.
    plants = []
    for row in all_plants:
        plant = {}
        plant["name"] = row["name"]
        todos = {k: row[k] for k in VALID_MONTH_NAMES}
        plant["todos"] = todos
        plants.append(plant)

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

        # Redirect user to home page
        return redirect("/")

    else:

        plants, selected_plants = prepare_plant_data(db, VALID_MONTH_NAMES)
        print(plants, file=sys.stderr)
        print(selected_plants, file=sys.stderr)

        return render_template(
            "planner.html", plants=plants, selected_plants=selected_plants
        )


@app.route("/weekly")
@login_required
def weekly():
    """Show the user a weekly summary of work to do in the garden."""

    return apology("TODO")


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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("must provide password", 400)

        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 400)

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
