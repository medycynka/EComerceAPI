from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone

from API.models import Order

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

    def sync_check_callback(self):
        """
        Actual callback running asynchronous
        """
        raise NotImplementedError("Can't call abstract sync_check_callback() function")

    def start(self):
        if not self.has_started:
            self.has_started = True
            self.__start_coroutine()

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

    def __start_coroutine(self) -> None:
        asyncio.run_coroutine_threadsafe(self.__async_check_callback(), self.loop)

    async def __async_check_callback(self) -> None:
        await asyncio.sleep(self.refresh_rate)
        await self.loop.run_in_executor(self.pool, self.sync_check_callback)

        self.__start_coroutine()


class NotifiesClientsWithUnpaidOrdersCollector(BaseAsyncTaskCollector):
    def sync_check_callback(self):
        """
        Send email to all users whose orders are due the following day
        """
        current_time_next_day = timezone.now() + timedelta(days=1)

        unpaid_orders = Order.objects.select_related('client').filter(
            status__in=Order.UNPAID_STATUS,
            payment_deadline__year=current_time_next_day.year,
            payment_deadline__month=current_time_next_day.month,
            payment_deadline__day=current_time_next_day.day
        ).values_list('full_price', 'client__email')

        from_email = settings.DEFAULT_EMAIL_ADDRESS

        if unpaid_orders.exists():
            send_mass_mail((
                (
                    'Unpaid order!',
                    f'You have one day left to pay for your order worth {order[0]}',
                    from_email,
                    [order[1]]
                ) for order in unpaid_orders
            ), fail_silently=True)


class ExpireUnpaidOrdersCollector(BaseAsyncTaskCollector):
    def sync_check_callback(self):
        """
        Set the status 'EXPIRED' for all unpaid orders whose payment deadline has already passed and inform users whose
        orders are overdue about it
        """
        current_time = timezone.now()

        expired_orders_emails = Order.objects.select_related('client').filter(
            status__in=Order.UNPAID_STATUS,
            payment_deadline__gte=current_time
        )

        from_email = settings.DEFAULT_EMAIL_ADDRESS

        if expired_orders_emails.exists():
            send_mass_mail((
                (
                    'Order expired!',
                    f'Your order has expired because you have not paid in full for your order',
                    from_email,
                    [order]
                ) for order in expired_orders_emails.values_list('client__email', flat=True)
            ), fail_silently=True)
            expired_orders_emails.update(status=Order.OrderStatus.EXPIRED)
