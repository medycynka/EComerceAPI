from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'API'

    def ready(self):
        from django.conf import settings
        if settings.USE_ASYNC_TASK_COLLECTOR:
            from API.async_task_collector import (
                NotifiesClientsWithUnpaidOrdersCollector,
                ExpireUnpaidOrdersCollector
            )

            async_task_collectors = [
                NotifiesClientsWithUnpaidOrdersCollector(),
                ExpireUnpaidOrdersCollector()
            ]
            # start collectors
            for task_collector in async_task_collectors:
                task_collector.start()
