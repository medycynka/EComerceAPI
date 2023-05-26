from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mass_mail

from django_extensions.management.jobs import DailyJob

from datetime import timedelta


class NotifiesClientsWithUnpaidOrders(DailyJob):
    help = "Send email to all users whose orders are due the following day."

    def execute(self):
        from API.models import Order

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
