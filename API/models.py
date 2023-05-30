from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.db import models
from django.db.models import F, QuerySet
from django.db.models import Avg
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User

from django_countries.fields import CountryField

from mptt.models import MPTTModel, TreeForeignKey

from API.managers import SoftDeleteManager
from API.managers import ProductManager
from API.managers import OrderManager

from PIL import Image
import os
from io import BytesIO
from datetime import timedelta
from decimal import Decimal


# region Abstract Core Models
class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, force=False):
        if force:
            super(SoftDeleteModel, self).delete(using=using, keep_parents=keep_parents)
        else:
            self.is_deleted = True
            self.save()
# endregion


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

    def get_ratings(self) -> float:
        if self.productrating_set.exists():
            return self.productrating_set.aggregate(ratings=Avg('rating'))['ratings']
        return 0.0


class ProductRating(models.Model):
    product = models.ForeignKey('API.Product', verbose_name=_("Product"), on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, verbose_name=_("Reviewer"), on_delete=models.CASCADE)
    review = models.TextField(verbose_name=_('Review'), blank=True, default=True)
    rating = models.FloatField(verbose_name=_("Rating"), blank=True, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(5.0)
    ])
    created_at = models.DateTimeField(verbose_name=_("Order date"), auto_now_add=True)

    class Meta:
        db_table = 'API_product_rating'
        verbose_name = 'product rating'
        verbose_name_plural = 'product ratings'
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


class Order(SoftDeleteModel):
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
    order_address = models.ForeignKey('API.Address', verbose_name=_("Order address"), null=True,
                                      on_delete=models.SET_NULL)
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
