from django.contrib import admin

from .models import User, Settings, Plants, SelectedPlants

admin.site.register(User)
admin.site.register(Settings)
admin.site.register(Plants)
admin.site.register(SelectedPlants)
