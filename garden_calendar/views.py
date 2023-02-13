from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import translation
from django.conf import settings

from .models import User, Plant

from .helpers.functions import prepare_plant_data


@login_required
def index(request):
    """Show the user-configured garden."""

    try:
        plants = User.objects.get(id=request.user.id).selected_plants.all()
        # TODO for internationalization, select the language, based on the user settings.
        plants = prepare_plant_data(plants, "si")
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
        user = User.objects.get(id=request.user.id)
        user.selected_plants.clear()
        for id in request.POST.keys():
            try:
                id = int(id)
                plant = Plant.objects.get(id=id)
                user.selected_plants.add(plant)
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
        # TODO for internationalization, select the language, based on the user settings.
        plants = prepare_plant_data(plants, "si")

        try:
            selected_plants = User.objects.get(id=request.user.id).selected_plants.all()
            selected_plants = [plant.id for plant in selected_plants]
        except ObjectDoesNotExist:
            # User has not selected any plants yet.
            selected_plants = []

        return render(
            request,
            "garden_calendar/planner.html",
            {"plants": plants, "selected_plants": selected_plants},
        )
