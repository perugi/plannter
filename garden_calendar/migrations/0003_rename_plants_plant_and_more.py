# Generated by Django 4.1.6 on 2023-02-07 07:21

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("garden_calendar", "0002_plants_settings_selectedplants"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Plants",
            new_name="Plant",
        ),
        migrations.RenameModel(
            old_name="SelectedPlants",
            new_name="SelectedPlant",
        ),
        migrations.RenameModel(
            old_name="Settings",
            new_name="Setting",
        ),
    ]