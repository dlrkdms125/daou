
from django.apps import AppConfig


class ChecksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "checks"

    def ready(self):
        from . import scheduler
        scheduler.start_if_enabled()
