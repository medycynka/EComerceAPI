from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q, QuerySet
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractDay
from django.db.models.functions import ExtractYear

from django_countries.fields import CountryField

from mptt.models import MPTTModel, TreeForeignKey

from PIL import Image
import os
from io import BytesIO
from datetime import timedelta, datetime
from decimal import Decimal


# region Products
class ProductCategory(MPTTModel):
    name = models.CharField(verbose_name=_("Category name"), max_length=128)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        db_table = 'API_product_category'
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name


class ProductManager(models.Manager):
    def products_by_seller(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        :param seller: user with 'seller' role
        :param filter_q: additional filtering expression
        :return: All products of given seller
        """
        q = self.get_queryset()

        if filter_q:
            q = q.filter(Q(seller=seller) & filter_q if seller.is_superuser else filter_q)
        else:
            q = q.all() if seller.is_superuser else q.filter(seller=seller)

        return q

    def counted_sales(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products annotated with the total number of copies sold
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products with the total number of copies sold
        """

        return self.products_by_seller(seller, filter_q).select_related('category').prefetch_related(
            'orderproductlistitem_set__order'
        ).annotate(
            sells_count=Coalesce(
                models.Sum('orderproductlistitem__quantity'),
                Cast(0, models.PositiveIntegerField())
            )
        )

    def top_sellers(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products in order from most to least frequently purchased
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from most to least frequently purchased
        """
        return self.counted_sales(seller, filter_q).order_by('-sells_count')

    def least_sellers(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products in order from least to most frequently purchased
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from least to most frequently purchased
        """
        return self.counted_sales(seller, filter_q).order_by('sells_count')

    def counted_profits(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products annotated with the total profit
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products with the total profit
        """
        return self.counted_sales(seller, filter_q).annotate(
            total_profit=Coalesce(
                F('price') * Cast(F('sells_count'), models.DecimalField(decimal_places=2, max_digits=18)),
                Cast(0.0, models.DecimalField(decimal_places=2, max_digits=24)),
                output_field=models.DecimalField(decimal_places=2, max_digits=24)
            )
        )

    def most_profitable(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products in order from most to least profitable
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from most to profitable
        """
        return self.counted_profits(seller, filter_q).order_by('-total_profit')

    def least_profitable(self, seller: User, filter_q: Q = None) -> QuerySet:
        """
        Get products in order from least to most profitable
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from least to most profitable
        """
        return self.counted_profits(seller, filter_q).order_by('total_profit')

    def available(self) -> QuerySet:
        """
        :return: Available products query with stock > 0
        """
        return self.get_queryset().filter(stock__gt=0)

    def out_of_stock(self) -> QuerySet:
        """
        :return: Not available products query with stock == 0
        """
        return self.get_queryset().filter(stock=0)


class Product(models.Model):
    name = models.CharField(verbose_name=_("Product name"), max_length=128)
    description = models.TextField(verbose_name=_("Product description"), blank=True, default='')
    price = models.DecimalField(verbose_name=_("Product price"), decimal_places=2, max_digits=6)   # up to 9999.99
    category = models.ForeignKey('API.ProductCategory', verbose_name=_("Product category"), null=True,
                                 on_delete=models.SET_NULL)
    photo = models.ImageField(verbose_name=_("Product photo"), upload_to='photos')
    thumbnail = models.ImageField(verbose_name=_("Product thumbnail"), upload_to='thumbnails', blank=True, default=None)
    seller = models.ForeignKey(User, verbose_name=_("Product seller"), null=True, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(verbose_name=_("Stock"), default=0)

    objects = ProductManager()

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'API_product'
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.create_thumbnail()

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def create_thumbnail(self):
        """
        Create a thumbnail image from provided `photo` file
        """

        thumbnail_name, thumbnail_extension = os.path.splitext(self.photo.name)
        thumbnail_extension = thumbnail_extension.lower()
        thumb_filename = thumbnail_name + '_thumbnail' + thumbnail_extension

        if self.thumbnail.name != thumb_filename:
            thumbnail = Image.open(self.photo)
            thumbnail.thumbnail(settings.THUMBNAIL_SIZE, Image.ANTIALIAS)

            if thumbnail_extension in ['.jpg', '.jpeg']:
                file_type = 'JPEG'
            elif thumbnail_extension == '.png':
                file_type = 'PNG'
            else:
                raise ValueError("Wrong product photo image! Accepted extensions are: jpg, jpeg or png!")

            temp_thumbnail = BytesIO()
            thumbnail.save(temp_thumbnail, file_type)
            temp_thumbnail.seek(0)

            self.thumbnail.save(thumb_filename, ContentFile(temp_thumbnail.read()), save=False)
            temp_thumbnail.close()
# endregion


# region Orders
class Address(models.Model):
    class PolishStates(models.IntegerChoices):
        """
        Polish voivodeship
        """
        NONE = 0, _('None')
        DS = 1, _('Dolnośląskie')
        KP = 2, _('Kujawsko-pomorskie')
        LB = 3, _('Lubelskie')
        LS = 4, _('Lubuskie')
        LD = 5, _('Łódzkie')
        MP = 6, _('Małopolskie')
        MZ = 7, _('Mazowieckie')
        OP = 8, _('Opolskie')
        PK = 9, _('Podkarpackie')
        PL = 10, _('Podlaskie')
        PM = 11, _('Pomorskie')
        SL = 12, _('Śląskie')
        SK = 13, _('Świętokrzyskie')
        WM = 14, _('Warmińsko-mazurskie')
        WP = 15, _('Wielkopolskie')
        ZP = 16, _('Zachodnio-pomorskie')

    country = CountryField(verbose_name=_("Country"))
    city = models.CharField(_("City"), max_length=128)
    street = models.CharField(_("Street"), max_length=128)
    street_number = models.CharField(_("Street number"), max_length=16)
    street_number_local = models.CharField(_("Street number local"), max_length=16, blank=True, default="")
    post_code = models.CharField(_("Postal code"), max_length=8)
    state = models.PositiveSmallIntegerField(_("Polish voivodeship"), choices=PolishStates.choices, blank=True,
                                             default=PolishStates.NONE)

    class Meta:
        db_table = "API_address"
        verbose_name = 'address'
        verbose_name_plural = 'addresses'

    def __str__(self):
        street_number_local = "/" + self.street_number_local if self.street_number_local else ""
        voivodeship = " woj. " + self.get_state_display() if self.state != Address.PolishStates.NONE else ""
        return f'{self.street} {self.street_number}{street_number_local}, {self.post_code} {self.city}, ' \
               f'{self.country.name}{voivodeship}'

    @property
    def short_address(self):
        street_number_local = "/" + self.street_number_local if self.street_number_local else ""
        return f'{self.street} {self.street_number}{street_number_local}, {self.post_code} {self.city}'

    @property
    def full_address(self):
        return self.__str__()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.country != "PL" and self.state != Address.PolishStates.NONE:
            self.state = Address.PolishStates.NONE
        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class OrderManager(models.Manager):
    def __combine_user_filter_q(self, user: User) -> Q:
        """
        :param user: user model
        :return: Q object representing query filter based on passed user
        """
        user_q = Q()
        if user.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists():
            user_q = Q(orderproductlistitem_set__product__seller=user)
        elif user.groups.filter(name=settings.USER_CLIENT_GROUP_NAME).exists():
            user_q = Q(client=user)
        return user_q

    def __annotate_sales_and_profits(self, queryset: QuerySet, group_key: str) -> QuerySet:
        """
        Group queryset by `group_key` and annotate corresponding groups its sales and profits
        :param queryset: orders queryset
        :param group_key: grouping key ex. 'months'
        :return: grouped queryset with annotated total sales and profits
        """
        return queryset.values(group_key).annotate(
            sales=models.Sum('orderproductlistitem__quantity'),
            profits=models.Sum(
                models.F('orderproductlistitem__quantity') * models.F('orderproductlistitem__product__price')
            )
        )

    def sales_by_day(self, user: User, date: datetime) -> QuerySet:
        """
        :param user: user model
        :param date: specific day in which we want to count sales and profits, ex 21-04-2023
        :return: total sales and profits in provided date
        """
        filter_q = Q(order_date__day=date.day) & Q(order_date__month=date.month) & Q(order_date__year=date.year)
        user_q = self.__combine_user_filter_q(user)

        if user_q:
            filter_q.add(user_q, Q.AND)

        q = self.get_queryset().filter(filter_q).prefetch_related('orderproductlistitem_set').annotate(
            day=ExtractDay('order_date')
        )

        return self.__annotate_sales_and_profits(q, 'day')

    def today_sales(self, user: User) -> QuerySet:
        """
        :param user: user model
        :return: total sales and profits in current date
        """
        return self.sales_by_day(user, timezone.now())

    def sales_by_month_days(self, user: User, month: int, year: int = None) -> QuerySet:
        """
        :param user: user model
        :param month: month
        :param year: year
        :return: total sales and profit for each day of the month
        """
        filter_q = Q(order_date__month=month) & Q(order_date__year=year)
        user_q = self.__combine_user_filter_q(user)

        if user_q:
            filter_q.add(user_q, Q.AND)

        q = self.get_queryset().filter(filter_q).prefetch_related('orderproductlistitem_set').annotate(
            day=ExtractDay('order_date')
        )

        return self.__annotate_sales_and_profits(q, 'day').order_by('day')

    def sales_by_months(self, user: User, year: int = None) -> QuerySet:
        """
        :param user: user model
        :param year: year
        :return: orders grouped by months with annotated total sales and profits in each month of provided year
        """
        if year is None:
            year = timezone.now().year  # if year is not provided, group by current years months
        filter_q = Q(order_date__year=year)
        user_q = self.__combine_user_filter_q(user)

        if user_q:
            filter_q.add(user_q, Q.AND)

        q = self.get_queryset().filter(filter_q).prefetch_related('orderproductlistitem_set').annotate(
            month=ExtractMonth('order_date')
        )

        return self.__annotate_sales_and_profits(q, 'month').order_by('month')

    def sales_by_years(self, user: User) -> QuerySet:
        """
        :param user: user model
        :return: orders grouped by years with annotated total sales and profits in each year
        """
        user_q = self.__combine_user_filter_q(user)

        if user_q:
            q = self.get_queryset().filter(user_q).prefetch_related('orderproductlistitem_set')
        else:
            q = self.get_queryset().prefetch_related('orderproductlistitem_set')

        q = q.annotate(year=ExtractYear('order_date'))

        return self.__annotate_sales_and_profits(q, 'year').order_by('year')

    def sales_by_countries(self, user: User) -> QuerySet:
        """
        :param user: user model
        :return: orders grouped by country of order address with annotated total sales and profits in each country
        """

        user_q = self.__combine_user_filter_q(user)

        if user_q:
            q = self.get_queryset().filter(user_q).prefetch_related(
                'orderproductlistitem_set', 'orderproductlistitem_set__product'
            ).select_related('order_address').annotate(country=F('order_address__country'))
        else:
            q = self.get_queryset().prefetch_related(
                'orderproductlistitem_set', 'orderproductlistitem_set__product'
            ).select_related('order_address').annotate(country=F('order_address__country'))

        return self.__annotate_sales_and_profits(q, 'country').order_by('-profits')


class Order(models.Model):
    class OrderStatus(models.IntegerChoices):
        """
        Order status:
            Pending: This means that the customer has begun the checkout process without making the necessary payments
            for the products.

            Pending Payment or Awaiting Payment: The customer may have initiated the payment process but is yet to
            pay for the product.

            Payment Received: This means that the customer has completed the payment for the order.

            Order Confirmed: This means that the customer has completed the payment and the order has been received
            and acknowledged by the e-commerce site.

            Failed: This means that the customer could not complete the payment or other verifications required to
            complete the order.

            Expired: The customer could not make the payment for the products within the stipulated payment window.

            Awaiting Fulfillment: This means that the customer has made the required payments for the price of the
            products, and the products shall now be shipped.

            Awaiting Shipment: This means that the products bought by the customer are now in a queue ready to be
            shipped and are waiting to be collected by the shipment service provider.

            On Hold: This means that the stock inventory is reduced by the number of products the customer has
            requested. However, other steps need to be completed for order fulfillment.

            Shipped: This means that the shipment provider has collected the products and the products are on their
            way to the customer.

            Partially Shipped: This means that only a part of the order or some products in the order are shipped.

            Awaiting Pickup: This means that the products have been shipped to either the customer-specified location
            or the business-specified location and are waiting to be picked up by the customer for delivery.

            Completed: This means that the product has been shipped and delivered, and the payment for the same has
            been made. The customer, at this point, can receive an invoice regarding the product they bought.

            Canceled: This might mean a variety of things. Both the seller and the customer may cancel an order.
            An order generally shows canceled if the customer fails to make the payment or if the seller has run out of
            stock of a particular product. Whether or not the customer is entitled to a refund of their money, in this
            case, depends on the stage of the order and other variables.

            Declined: The seller declares that they cannot ship and fulfill the order.

            Refunded: The seller agrees to refund the amount paid by the customer to buy the product.

            Partially Refunded: The seller partially refunds the amount paid by the customer while buying the product.

            Refund Rejected: The seller refuses to process the entire or partial refund of the amount paid by the
            customer at the time of buying the products.

            Disputed: The customer has raised an issue with the order fulfillment or the refund procedure. Generally,
            customers raise disputes when e-commerce websites refuse to refund the amount paid by them.
        """
        PENDING = 0, _('Pending')
        PENDING_PAYMENT = 1, _('Pending Payment')
        PAYMENT_RECEIVED = 2, _('Payment Received')
        ORDER_CONFIRMED = 3, _('Order Confirmed')
        FAILED = 4, _('Failed')
        EXPIRED = 5, _('Expired')
        AWAITING_FULFILLMENT = 6, _('Awaiting Fulfillment')
        AWAITING_SHIPMENT = 7, _('Awaiting Shipment')
        ON_HOLD = 8, _('On Hold')
        SHIPPED = 9, _('Shipped')
        PARTIALLY_SHIPPED = 10, _('Partially Shipped')
        AWAITING_PICKUP = 11, _('Awaiting Pickup')
        COMPLETED = 12, _('Completed')
        CANCELED = 13, _('Canceled')
        DECLINED = 14, _('Declined')
        REFUNDED = 15, _('Refunded')
        PARTIALLY_REFUNDED = 16, _('Partially Refunded')
        REFUND_REJECTED = 17, _('Refund Rejected')
        DISPUTED = 18, _('Disputed')

    UNPAID_STATUS = [OrderStatus.PENDING, OrderStatus.PENDING_PAYMENT, OrderStatus.EXPIRED]

    client = models.ForeignKey(User, verbose_name=_("Client"), null=True, on_delete=models.SET_NULL)
    order_address = models.ForeignKey('API.Address', verbose_name=_("Order address"), null=True, on_delete=models.SET_NULL)
    order_date = models.DateTimeField(verbose_name=_("Order date"), blank=True)
    payment_deadline = models.DateTimeField(verbose_name=_('Payment deadline'), blank=True)
    full_price = models.DecimalField(verbose_name=_('Order summary price'), blank=True, null=True, decimal_places=2,
                                     max_digits=20)
    is_paid = models.BooleanField(verbose_name=_('Is order paid?'), blank=True, default=False)
    status = models.PositiveSmallIntegerField(_("Order status"), choices=OrderStatus.choices, blank=True,
                                              default=OrderStatus.PENDING)
    discount = models.DecimalField(verbose_name=_('Order discount'), blank=True, null=True, decimal_places=2,
                                   max_digits=3, default=0.0)

    objects = OrderManager()

    class Meta:
        db_table = "API_order"

    @property
    def products_list(self) -> QuerySet:
        """
        :return: :model:`Common.Product` list associated with this order
        """
        return OrderProductListItem.objects.select_related('product', 'product__category').filter(
            order=self
        ).only('product', 'quantity')

    @property
    def has_discount(self) -> bool:
        """
        :return: check if this order has discount
        """
        return self.discount > Decimal(0.0)

    @property
    def final_price(self) -> Decimal:
        """
        :return: final order price with discount included ex. for 20% discount final price would be 80% of total price
        """
        return self.full_price * (Decimal(1.0) - self.discount) if self.has_discount else self.full_price

    @property
    def status_name(self) -> str:
        """
        Property wrapper for GraphQl schema types
        """
        return self.get_status_display()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, update_full_price=False):
        if not self.order_date:
            self.order_date = timezone.now()
        if not self.payment_deadline:
            self.payment_deadline = self.order_date + timedelta(days=settings.PAYMENT_DEADLINE_DAYS)
        if update_full_price and not self.full_price and self.products_list.exists():
            self.full_price = self.products_list.aggregate(
                full_price=models.Sum(F('product__price') * F('quantity'), output_field=models.DecimalField())
            )['full_price']

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class OrderProductListItem(models.Model):
    """
    Representation of the relationship between the product and the order taking into account the
    quantity of the related product
    """
    order = models.ForeignKey('API.Order', verbose_name=_("Order"), on_delete=models.CASCADE)
    product = models.ForeignKey('API.Product', verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"), blank=True, default=1,
                                           validators=[MinValueValidator(1)])

    class Meta:
        db_table = "API_order_product_list_item"


class DiscountCoupon(models.Model):
    class ValidTime(models.IntegerChoices):
        """
        How long this coupon is valid, ex 7 days
        """
        ONE_DAY = 1, _('One day')
        THREE_DAYS = 3, _('Three days')
        ONE_WEEK = 7, _('One week')
        TWO_WEEKS = 14, _('Two weeks')
        ONE_MONTH = 30, _('One month')
        THREE_MONTHS = 91, _('Three months')
        ONE_YEAR = 365, _('Ono year')

    code = models.CharField(verbose_name=_("Coupon code"), max_length=32)
    is_used = models.BooleanField(verbose_name=_('Id coupon used?'), blank=True, default=False)
    is_expired = models.BooleanField(verbose_name=_('Id coupon expired?'), blank=True, default=False)
    valid_time = models.PositiveSmallIntegerField(_("Valid time"), choices=ValidTime.choices, blank=True,
                                                  default=ValidTime.ONE_DAY)
    valid_date = models.DateTimeField(verbose_name=_('Payment deadline'), blank=True)
    discount = models.DecimalField(verbose_name=_('Discount'), blank=True, null=True, decimal_places=2,
                                   max_digits=3, default=0.0)

    class Meta:
        db_table = "API_discount_coupon"

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.valid_date:
            self.valid_date = timezone.now() + timedelta(days=self.valid_time)

        super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
# endregion
