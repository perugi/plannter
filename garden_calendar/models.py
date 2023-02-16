from django.db import models
from django.contrib.auth.models import AbstractUser

from .helpers.constants import LANGUAGES


class User(AbstractUser):
    selected_plants = models.ManyToManyField("Plant")
    language = models.CharField(max_length=2, choices=LANGUAGES, default="en")
    notifications = models.CharField(max_length=27, default="")


class Plant(models.Model):
    creator = models.ForeignKey("User", on_delete=models.CASCADE)
    name_en = models.CharField(max_length=64)
    name_si = models.CharField(max_length=64)
    todos = models.CharField(max_length=110, default="")

    def __str__(self):
        return f"{self.name_si}: [{self.creator}]"


class AddEMail(models.Model):
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    email = models.EmailField()

    def __str__(self):
        return f"{self.mail} [{self.user}]"
