from django.apps import AppConfig


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_activity'

    def ready(self):
        from . import signals
        from . import init_tasks
