import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "amrdevs.settings")

app = Celery("amrdevs")

# 🔴 THIS LINE IS CRITICAL
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
