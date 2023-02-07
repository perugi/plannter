from django.contrib import admin

from .models import User, Setting, Plant, SelectedPlant

admin.site.register(User)
admin.site.register(Setting)
admin.site.register(Plant)
admin.site.register(SelectedPlant)
