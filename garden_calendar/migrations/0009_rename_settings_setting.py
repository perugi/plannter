# Generated by Django 4.1.6 on 2023-02-14 09:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "garden_calendar",
            "0008_remove_user_language_remove_user_selected_plants_and_more",
        ),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Settings",
            new_name="Setting",
        ),
    ]