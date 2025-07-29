# tippanee/apps.py
from django.apps import AppConfig


class DjangoTippaneeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_tippanee"

    def ready(self):
        import django_tippanee.signals
