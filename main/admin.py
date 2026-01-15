from django.contrib import admin
from django.apps import apps
from django.db import models

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
from .models import JSONImport

@admin.register(JSONImport)
class JSONImportAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False  # Hide the "Add" button

    def changelist_view(self, request, extra_context=None):
        return redirect(reverse('json_data_loader'))  # Highlighted with another colour at the top

# Register your models here.
all_models = apps.get_models()
admin.header = "AmrDevs Administration"
admin.site.site_title = "AmrDevs Admin Portal"
admin.site.index_title = "Welcome to AmrDevs Admin Portal"
admin.site.site_header = "AmrDevs Admin"

MY_APPS = {
    "jobportal",
    "accounts",
    "core",
}

for model in all_models:

    app_label = model._meta.app_label
    #Skip third-party & Django contrib apps
    if app_label not in MY_APPS:
        continue

    try:
        class Admin(admin.ModelAdmin):
            list_display = [field.name for field in model._meta.fields]
            search_fields = [field.name for field in model._meta.fields if isinstance(field, (models.CharField, models.TextField))]
        
        admin.site.register(model, Admin)
    except admin.sites.AlreadyRegistered:
        pass
