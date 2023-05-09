from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone
from django.utils.text import gettext_lazy as _
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast

from PIL import Image
import os
from io import BytesIO
from datetime import timedelta

# Create your models here.


class ProductCategory(models.Model):
    name = models.CharField(verbose_name=_("Category name"), max_length=128)

    class Meta:
        db_table = 'Common_product_category'
        verbose_name = 'product category'
        verbose_name_plural = 'product categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name=_("Product name"), max_length=128)
    description = models.TextField(verbose_name=_("Product description"), blank=True, default='')
    price = models.DecimalField(verbose_name=_("Product price"), decimal_places=2, max_digits=6)   # up to 9999.99
    category = models.ForeignKey(ProductCategory, verbose_name=_("Product category"), null=True,
                                 on_delete=models.SET_NULL)
    photo = models.ImageField(verbose_name=_("Product photo"), upload_to='photos')
    thumbnail = models.ImageField(verbose_name=_("Product thumbnail"), upload_to='thumbnails', blank=True, default=None)
    seller = models.ForeignKey(User, verbose_name=_("Product seller"), null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Common_product'
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.create_thumbnail()

        super(Product, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                  update_fields=update_fields)

    def create_thumbnail(self):
        """
        Create a thumbnail image from provided `photo` file
        """

        thumbnail = Image.open(self.photo)
        thumbnail.thumbnail(settings.THUMBNAIL_SIZE, Image.ANTIALIAS)

        thumbnail_name, thumbnail_extension = os.path.splitext(self.photo.name)
        thumbnail_extension = thumbnail_extension.lower()
        thumb_filename = thumbnail_name + '_thumbnail' + thumbnail_extension

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

    @staticmethod
    def products_by_seller(seller, filter_q=None):
        """
        Get filtered products for given seller
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: given sellers' products
        """
        q = Product.objects.select_related('category').prefetch_related('orderproductlistitem_set__order')

        if filter_q:
            q = q.filter(Q(seller=seller) & filter_q if seller.is_superuser else filter_q)
        else:
            q = q.all() if seller.is_superuser else q.filter(seller=seller)

        return q

    @staticmethod
    def top_sellers(seller, filter_q=None):
        """
        Get products in order from most to least frequently purchased
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from most to least frequently purchased
        """
        q = Product.products_by_seller(seller, filter_q)

        return q.annotate(
            sells_count=Coalesce(models.Sum('orderproductlistitem__quantity'), Cast(0, models.PositiveIntegerField()))
        ).order_by('-sells_count')

    @staticmethod
    def least_sellers(seller, filter_q=None):
        """
        Get products in order from least to most frequently purchased
        :param seller: user model representing 'seller'
        :param filter_q: optional filter for filtering products list before ordering based on purchased counts (ex. get
        list of products form date range)
        :return: products in order from least to most frequently purchased
        """
        q = Product.products_by_seller(seller, filter_q)

        return q.annotate(
            sells_count=Coalesce(models.Sum('orderproductlistitem__quantity'), Cast(0, models.PositiveIntegerField()))
        ).order_by('sells_count')


class Order(models.Model):
    client = models.ForeignKey(User, verbose_name=_("Client"), null=True, on_delete=models.SET_NULL)
    order_address = models.CharField(verbose_name=_("Order address"), max_length=255)
    order_date = models.DateTimeField(verbose_name=_("Order date"), blank=True)
    payment_deadline = models.DateTimeField(verbose_name=_('Payment deadline'), blank=True)
    full_price = models.DecimalField(verbose_name=_('Order summary price'), blank=True, null=True, decimal_places=2,
                                     max_digits=20)
    is_paid = models.BooleanField(verbose_name=_('Id order paid?'), blank=True, default=False)

    @property
    def products_list(self):
        """
        :return: :model:`Common.Product` list associated with this order
        """
        return OrderProductListItem.objects.select_related('product', 'product__category').filter(
            order=self
        ).only('product', 'quantity')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.order_date:
            self.order_date = timezone.now()
        if not self.payment_deadline:
            self.payment_deadline = self.order_date + timedelta(days=settings.PAYMENT_DEADLINE_DAYS)
        if not self.full_price and self.products_list.exists():
            self.full_price = self.products_list.aggregate(
                full_price=models.Sum(F('product__price') * F('quantity'), output_field=models.DecimalField())
            )['full_price']

        super(Order, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                update_fields=update_fields)


class OrderProductListItem(models.Model):
    """
    Representation of the relationship between the product and the order taking into account the
    quantity of the related product
    """
    order = models.ForeignKey(Order, verbose_name=_("Order"), on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"), blank=True, default=1,
                                           validators=[MinValueValidator(1)])

    class Meta:
        db_table = "Common_order_product_list_item"
