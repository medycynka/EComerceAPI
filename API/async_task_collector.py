from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone

from Common.models import Order

from datetime import timedelta
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor


class BaseAsyncTaskCollector:
    def __init__(self):
        self.refresh_rate = settings.TASK_COLLECTOR_REFRESH_RATE
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.loop = asyncio.get_event_loop()
        self.runner = threading.Thread(target=self.loop.run_forever)
        self.runner.daemon = True
        self.runner.start()
        self.has_started = False

    def __del__(self):
        self.stop()

    def start(self):
        """
        Example implementation logic

        if not self.has_started:
            self.has_started = True
            start initial coroutine using `asyncio.run_coroutine_threadsafe` and `self.loop`
        """
        raise NotImplementedError("Can't call abstract start() function")

    def stop(self):
        if self.runner is not None and self.runner.is_alive():
            self.runner.join()

        if self.pool is not None:
            self.pool.shutdown(wait=False)

        if self.loop is not None:
            self.loop.close()

    def restart(self):
        self.pool = ThreadPoolExecutor(max_workers=1)
        self.loop = asyncio.get_event_loop()
        self.runner = threading.Thread(target=self.loop.run_forever)
        self.runner.daemon = True
        self.runner.start()
        self.has_started = False
        self.start()


class NotifiesClientsWithUnpaidOrdersCollector(BaseAsyncTaskCollector):
    def start(self):
        if not self.has_started:
            self.has_started = True
            self.__start_check_unpaid_orders_coroutine()

    def __check_unpaid_orders_sync(self):
        current_time_next_day = timezone.now() + timedelta(days=1)

        unpaid_orders = Order.objects.select_related('client').filter(
            is_paid=False,
            payment_deadline__year=current_time_next_day.year,
            payment_deadline__month=current_time_next_day.month,
            payment_deadline__day=current_time_next_day.day
        )

        from_email = settings.DEFAULT_EMAIL_ADDRESS

        if unpaid_orders.exists():
            send_mass_mail((
                (
                    'Unpaid order!',
                    f'You have one day left to pay for your order worth {order.full_price}',
                    from_email,
                    [order.client.email]
                ) for order in unpaid_orders
            ), fail_silently=True)

    def __start_check_unpaid_orders_coroutine(self) -> None:
        asyncio.run_coroutine_threadsafe(self.__check_unpaid_orders_async(), self.loop)

    async def __check_unpaid_orders_async(self) -> None:
        await asyncio.sleep(self.refresh_rate)
        await self.loop.run_in_executor(self.pool, self.__check_unpaid_orders_sync)

        self.__start_check_unpaid_orders_coroutine()
