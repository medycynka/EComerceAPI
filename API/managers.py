from django.db import models
from django.db.models import F, Q, QuerySet
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractDay
from django.db.models.functions import ExtractYear
from django.conf import settings
from django.utils import timezone

from datetime import datetime


class SoftDeleteQuerySet(QuerySet):
    def delete(self, force=False):
        """
        'Delete' the records in the current QuerySet by setting is_deleted to True.
        :param force: force delete - if True perform actual delete in db ex. for admin management
        """
        if force:
            super().delete()
        else:
            self.update(is_deleted=True)


class SoftDeleteManager(models.manager.BaseManager.from_queryset(SoftDeleteQuerySet)):
    def get_queryset(self, with_deleted: bool = False) -> QuerySet:
        if with_deleted:
            return super().get_queryset()
        return super().get_queryset().filter(is_deleted=False)

    def deleted(self) -> QuerySet:
        return self.get_queryset(with_deleted=True).filter(is_deleted=True)


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


class OrderManager(SoftDeleteManager):
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

    def unpaid(self) -> QuerySet:
        return self.get_queryset().filter(Q(is_paid=False) | Q(status__in=self.model.UNPAID_STATUS))

    def expired(self) -> QuerySet:
        return self.get_queryset().filter(status__in=self.model.OrderStatus.EXPIRED)

    def completed(self) -> QuerySet:
        return self.get_queryset().filter(status__in=self.model.OrderStatus.COMPLETED)
