# Generated by Django 4.1.6 on 2023-02-13 21:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("garden_calendar", "0006_user_selected_plants_delete_selectedplant"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="language",
            field=models.CharField(
                choices=[("en", "English"), ("si", "Slovenian")],
                default="en",
                max_length=2,
            ),
        ),
        migrations.DeleteModel(
            name="Setting",
        ),
    ]
