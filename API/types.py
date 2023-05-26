from django.contrib.auth import get_user_model

import graphene
from graphene_django import DjangoObjectType

from django_countries.graphql.types import Country

from API.models import ProductCategory
from API.models import Product
from API.models import Address
from API.models import Order
from API.models import OrderProductListItem
from API.models import DiscountCoupon


class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'seller', 'stock')


class ProductStatisticType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'seller', 'stock')

    sells_count = graphene.Int()
    total_profit = graphene.Decimal()


class AddressType(DjangoObjectType):
    country = graphene.Field(Country)

    class Meta:
        model = Address
        fields = ('id', 'country', 'city', 'street', 'street_number', 'street_number_local', 'post_code', 'state')

    short_address = graphene.String()
    full_address = graphene.String()


class OrderProductListItemType(DjangoObjectType):
    class Meta:
        model = OrderProductListItem
        fields = ('id', 'product', 'quantity')


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ('id', 'client', 'order_address', 'order_date', 'payment_deadline', 'full_price', 'is_paid', 'status',
                  'discount')
        convert_choices_to_enum = False

    status_name = graphene.String()
    products_list = graphene.List(OrderProductListItemType)
    has_discount = graphene.Boolean()
    final_price = graphene.Decimal()


class SalesAndProfitsType(graphene.ObjectType):
    total_sales = graphene.BigInt()
    total_profits = graphene.Decimal()


class MonthlySalesAndProfitsType(graphene.ObjectType):
    month = graphene.Int()
    sales = graphene.BigInt()
    profits = graphene.Decimal()


class CountrySalesAndProfitsType(graphene.ObjectType):
    country = graphene.String()
    sales = graphene.BigInt()
    profits = graphene.Decimal()


class DiscountCouponType(DjangoObjectType):
    class Meta:
        model = DiscountCoupon
        fields = ('id', 'code', 'is_used', 'is_expired', 'valid_time', 'valid_date', 'discount')
        convert_choices_to_enum = False
