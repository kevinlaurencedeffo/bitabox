from django.apps import AppConfig


class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bita_app'

    def ready(self):
        import bita_app.signals
