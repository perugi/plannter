from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import translation

from .helpers.constants import WEEK_DAYS
from .helpers.functions import prepare_plant_data, prepare_weekly_todos, send_summary
from .models import Plant, User, AddEMail


@login_required
def index(request):
    """Show the user-configured garden."""

    try:
        plants = request.user.selected_plants.all()
        plants = prepare_plant_data(plants, request.user.language)
    except ObjectDoesNotExist:
        # User has not selected any plants yet.
        plants = []

    translation.activate(request.user.language)

    return render(request, "garden_calendar/index.html", {"plants": plants})


def login_view(request):
    if request.method == "POST":
        # Get the u/p and attempt to sign the user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, "Invalid username and/or password.")
            return render(
                request,
                "garden_calendar/login.html",
            )

    else:
        return render(request, "garden_calendar/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]

        # Ensure password matches confirmation
        if password != confirmation:
            messages.error(request, "Passwords must match.")
            return render(
                request,
                "garden_calendar/register.html",
            )

        # Attempt to create a new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            messages.error(request, "Username already taken.")
            return render(
                request,
                "garden_calendar/register.html",
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "garden_calendar/register.html")


@login_required
def password_change(request):
    """Allow the user to change their password"""

    if request.method == "POST":
        password_old = request.POST["password_old"]
        password_new = request.POST["password_new"]
        password_confirm = request.POST["password_confirm"]

        # Ensure all the passwords were submitted
        if not password_old or not password_new or not password_confirm:
            messages.error(request, "Please fill out all the password fields.")
            return render(request, "garden_calendar/password_change.html")

        # Get the u/p and attempt to sign the user in
        username = request.user.username
        user = authenticate(request, username=username, password=password_old)

        # Check if authentication successful
        if user is None:
            messages.error(request, "Old password is invalid.")
            return render(
                request,
                "garden_calendar/password_change.html",
            )

        # Ensure the password and its confirmation matches
        elif password_new != password_confirm:
            messages.error(request, "New password and confirmation do not match.")
            return render(
                request,
                "garden_calendar/password_change.html",
            )

        # set_password also hashes the password that the user will get
        user.set_password(password_new)
        user.save()
        login(request, user)

        messages.success(request, "Password successfully updated.")
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "garden_calendar/password_change.html")


@login_required
def planner(request):
    """Plan the garden by selecting the plants to be grown."""

    if request.method == "POST":
        # Clear the existing selected plants and proceed to add the ones that were selected in the POST request.
        request.user.selected_plants.clear()
        for id in request.POST.keys():
            try:
                id = int(id)
                plant = Plant.objects.get(id=id)
                request.user.selected_plants.add(plant)
            except ValueError:
                # If we fail the conversion to int, we're looking at the csrf token.
                pass
            except ObjectDoesNotExist:
                messages.warning(request, f"Plant id {id} not found.")
                continue

        messages.success(request, "Garden successfully updated!")

        return HttpResponseRedirect(reverse("index"))

    else:
        plants = Plant.objects.all().filter(creator_id__in=[1, request.user.id])
        plants = prepare_plant_data(plants, request.user.language)

        try:
            selected_plants = request.user.selected_plants.all()
            selected_plants = [plant.id for plant in selected_plants]
        except ObjectDoesNotExist:
            # User has not selected any plants yet.
            selected_plants = []

        return render(
            request,
            "garden_calendar/planner.html",
            {"plants": plants, "selected_plants": selected_plants},
        )


class SettingsForm(ModelForm):
    class Meta:
        model = User
        fields = ["language"]
        language = {"language": ""}


@login_required
def settings(request):
    """Allow the user to change the account settings."""

    if request.method == "POST":
        form = SettingsForm(request.POST)
        if form.is_valid():
            request.user.language = request.POST["language"]

            # Process the default e-mail (store in User).
            if not request.POST.get("email_1"):
                messages.error(request, f"Please provide a default e-mail")
                return HttpResponseRedirect(reverse("settings"))

            request.user.email = request.POST.get("email_1")

            # Process any additional emails (store in AddEMail)
            AddEMail.objects.filter(user=request.user).delete()

            for i in range(2, 6):
                if request.POST.get(f"email_{i}"):
                    email = AddEMail(
                        user=request.user, email=request.POST.get(f"email_{i}")
                    )
                    email.save()

            # Get the notification days, selected by the user and format them into a comma separated
            # string, to be stored in the user database.
            notifications = ""
            for key in request.POST.keys():
                if key[:6] != "notify":
                    continue
                else:
                    notifications += key[7:] + ","
            request.user.notifications = notifications[:-1]

            request.user.save()

            # Notification for the user that the settings have been updated.
            messages.success(request, f"Settings successfully updated!")
            return HttpResponseRedirect(reverse("index"))
        else:
            messages.error(request, f"Invalid settings sent!")
            return HttpResponseRedirect(reverse("settings"))

    # The default mail is saved in the User model, additional in the AddEMail.
    emails = [request.user.email]
    emails += [object.email for object in AddEMail.objects.filter(user=request.user)]

    notifications = {}
    for day in WEEK_DAYS:
        notifications[day] = False

    # Generate a dictionary with a key for each day, True if notification is set, False if not.
    try:
        set_notifications = request.user.notifications.split(",")
    except AttributeError:
        set_notifications = []
    notifications = {}
    for day in WEEK_DAYS:
        if day in set_notifications:
            notifications[day] = True
        else:
            notifications[day] = False

    language = request.user.language

    return render(
        request,
        "garden_calendar/settings.html",
        {
            "no_emails": len(emails),
            "emails": emails,
            "notifications": notifications,
            "language": language,
        },
    )


@login_required
def weekly(request):
    """Show the user a weekly summary of work to do in the garden."""

    try:
        plants = request.user.selected_plants.all()
        plants = prepare_plant_data(plants, request.user.language)
    except ObjectDoesNotExist:
        # User has not selected any plants yet.
        plants = []

    weekly_todos = prepare_weekly_todos(plants)

    if request.method == "POST":
        send_summary(request, weekly_todos)

        messages.success(
            request, f"Summary sent to the e-mails, configured in your settings."
        )

    return render(
        request,
        "garden_calendar/weekly.html",
        {"weekly_todos": weekly_todos, "plants": plants},
    )
