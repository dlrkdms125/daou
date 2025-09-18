# mail/apps.py
from django.apps import AppConfig

class MailConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mail"

    def ready(self):
        # 앱이 로딩된 뒤에 scheduler 시작 (순환참조 방지 위해 함수 안에서 import)
        from checks.scheduler import start_if_enabled
        start_if_enabled
