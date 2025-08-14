
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eschecker.settings")

app = Celery("eschecker")
app.config_from_object("django.conf:settings", namespace="CELERY")

# Beat schedule: every minute
app.conf.beat_schedule = {
    "pull-elasticsearch-every-minute": {
        "task": "checks.tasks.pull_or_seed",
        "schedule": 60.0,
    },
}

app.autodiscover_tasks()
