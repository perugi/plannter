from django.db import models
from django.contrib.auth.models import AbstractUser

from helpers.constants import LANGUAGES


class User(AbstractUser):
    pass


class Settings(models.model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    pass


class Plants(models.model):
    # user_id, id, name_si, name_en, todos
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    name_en = models.CharField(max_length=64)
    name_si = models.CharField(max_length=64)
    todos = models.CharField
    time_modified = models.DateTimeField(auto_now_add=True)


class SelectedPlants(models.model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    selected_plants = models.ManyToManyField("Plants")
