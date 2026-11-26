from django.apps import AppConfig


class PortafolioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portafolio"
    verbose_name = "Casos de estudio"

    def ready(self):
        from . import signals  # noqa: F401
