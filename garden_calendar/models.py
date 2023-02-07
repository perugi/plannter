from django.db import models
from django.contrib.auth.models import AbstractUser

from .helpers.constants import LANGUAGES


class User(AbstractUser):
    pass


class Setting(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    pass


class Plant(models.Model):
    # user_id, id, name_si, name_en, todos
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    name_en = models.CharField(max_length=64)
    name_si = models.CharField(max_length=64)
    todos = models.CharField
    time_modified = models.DateTimeField(auto_now_add=True)


class SelectedPlant(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    selected_plants = models.ManyToManyField("Plant")
