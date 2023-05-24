from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mass_mail

from django_extensions.management.jobs import DailyJob


class ExpireUnpaidOrders(DailyJob):
    help = "Set the status 'EXPIRED' for all unpaid orders whose payment deadline has already passed and inform " \
           "users whose orders are overdue about it."

    def execute(self):
        from API.models import Order

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
