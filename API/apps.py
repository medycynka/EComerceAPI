from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'API'

    def ready(self):
        from django.conf import settings
        if settings.USE_ASYNC_TASK_COLLECTOR:
            from API.async_task_collector import NotifiesClientsWithUnpaidOrdersCollector

            async_task_collector = NotifiesClientsWithUnpaidOrdersCollector()
            # start collector
            async_task_collector.start()
