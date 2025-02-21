from django.contrib import admin
from django.apps import apps
from django.db import models
# Register your models here.
all_models = apps.get_models()

for model in all_models:
    try:
        class Admin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
            search_fields = [field.name for field in model._meta.fields if isinstance(field, (models.CharField, models.TextField))]
        
        admin.site.register(model, Admin)
    except admin.sites.AlreadyRegistered:
        pass