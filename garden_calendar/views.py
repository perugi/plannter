from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from .models import User, Plant, SelectedPlant, Setting

from .helpers.functions import prepare_plant_data


@login_required
def index(request):
    """Show the user-configured garden."""

    try:
        plants = SelectedPlant.objects.get(user=request.user).selected_plants.all()
        plants = prepare_plant_data(plants, "si")
    except ObjectDoesNotExist:
        # User has not selected any plants yet.
        plants = []

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
            return render(
                request,
                "garden_calendar/login.html",
                {"message": "Invalid username and/or password."},
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
            return render(
                request,
                "garden_calendar/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create a new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "garden_calendar/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "garden_calendar/register.html")
