from django.db import models
from django.db.models import F, Q, QuerySet, Avg, Count
from django.contrib.auth.models import User
from django.db.models.functions import Coalesce
from django.db.models.functions import Cast
from django.db.models.functions import ExtractMonth
from django.db.models.functions import ExtractDay
from django.db.models.functions import ExtractYear
from django.conf import settings
from django.utils import timezone

from datetime import datetime
from typing import Union, Tuple, List
import sys


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
    EPSILON = sys.float_info.epsilon

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
            'orderproductlistitem_set'
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

    def with_ratings(self) -> QuerySet:
        """
        Get products annotated with average ratings
        """
        return self.get_queryset().prefetch_related('productrating_set').annotate(
            ratings=Coalesce(Avg('productrating__rating'), Cast(0.0, models.FloatField())),
            rates_count=Count('productrating__rating')
        )

    def n_star_rating(self, stars: Union[Tuple[float, float], List[float]]) -> QuerySet:
        """
        Get products filtered by provided ratings range
        :param stars: ratings range [min, max]
        :return: products annotated with ratings in provided  range
        """
        if len(stars):
            if len(stars) == 1:
                stars = (stars[0], 5.0)
            if stars[0] < 0.0 or stars[0] > 5.0:
                raise ValueError("'min' value error! Product ratings are from 0 to 5.")
            if stars[1] < 0.0 or stars[1] > 5.0:
                raise ValueError("'max' value error! Product ratings are from 0 to 5.")
            return self.with_ratings().filter(Q(ratings__gte=stars[0]) & Q(ratings__lte=stars[1]))
        raise ValueError("Empty 'stars' argument!")

    def zero_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '0 star' rated products
        :param with_half: should query include half values, if yes returns stars range [0.0, 0.5]
        :return: products with '0 star' ratings
        """
        if with_half:
            return self.n_star_rating((0.0, 0.5))
        return self.n_star_rating((0.0, self.EPSILON))

    def one_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '1 star' rated products (without half stars ex 1.5)
        :param with_half: should query include half values, if yes returns stars range [0.5, 1.5]
        :return: products with '1 star' ratings
        """
        if with_half:
            return self.n_star_rating((0.5, 1.5))
        return self.n_star_rating((0.5 + self.EPSILON, 1.5 - self.EPSILON))

    def two_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '2 star' rated products (without half stars ex 1.5)
        :param with_half: should query include half values, if yes returns stars range [1.5, 2.5]
        :return: products with '2 star' ratings
        """
        if with_half:
            return self.n_star_rating((1.5, 2.5))
        return self.n_star_rating((1.5 + self.EPSILON, 2.5 - self.EPSILON))

    def three_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '3 star' rated products (without half stars ex 3.5)
        :param with_half: should query include half values, if yes returns stars range [2.5, 3.5]
        :return: products with '3 star' ratings
        """
        if with_half:
            return self.n_star_rating((2.5, 3.5))
        return self.n_star_rating((2.5 + self.EPSILON, 3.5 - self.EPSILON))

    def four_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '4 star' rated products (without half stars ex 4.5)
        :param with_half: should query include half values, if yes returns stars range [3.5, 4.5]
        :return: products with '4 star' ratings
        """
        if with_half:
            return self.n_star_rating((3.5, 4.5))
        return self.n_star_rating((3.5 + self.EPSILON, 4.5 - self.EPSILON))

    def five_stars(self, with_half: bool = False) -> QuerySet:
        """
        Wrapper for 'n_star_rating' for getting '5 star' rated products (without half stars ex 4.5)
        :param with_half: should query include half values, if yes returns stars range [4.5, 5.0]
        :return: products with '5 star' ratings
        """
        if with_half:
            return self.n_star_rating((4.5, 5.0))
        return self.n_star_rating((4.5 + self.EPSILON, 5.0))

    def with_views(self) -> QuerySet:
        """
        Get products annotated with number of views
        """
        return self.get_queryset().prefetch_related('productview_set').annotate(views=Count('productview'))

    def full_stats(self, filter_q: Q = None) -> QuerySet:
        q = self.get_queryset()

        if filter_q:
            q = q.filter(filter_q)

        return q.prefetch_related('orderproductlistitem_set', 'productrating_set', 'productview_set').annotate(
            sells_count=Coalesce(models.Sum('orderproductlistitem__quantity'), Cast(0, models.PositiveIntegerField())),
            total_profit=Coalesce(
                F('price') * Cast(F('sells_count'), models.DecimalField(decimal_places=2, max_digits=18)),
                Cast(0.0, models.DecimalField(decimal_places=2, max_digits=24)),
                output_field=models.DecimalField(decimal_places=2, max_digits=24)
            ),
            ratings=Coalesce(Avg('productrating__rating'), Cast(0.0, models.FloatField())),
            rates_count=Count('productrating__rating'),
            views=Count('productview')
        )


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
