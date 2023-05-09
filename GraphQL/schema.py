from django.db.models import Q

import graphene
from graphene_django import DjangoObjectType

from API.models import ProductCategory
from API.models import Product
from API.models import Order


class ProductCategoryType(DjangoObjectType):
    class Meta:
        model = ProductCategory
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class ProductStatisticType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"

    sells_count = graphene.Int()


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


def get_date_range_product_filter_from_kwargs(**kwargs):
    date_from_limit = kwargs.get("date_from", None)
    date_to_limit = kwargs.get("date_to", None)

    date_filter_query = Q()

    if date_from_limit:
        date_filter_query.add(Q(orderproductlistitem__order__order_date__gte=date_from_limit), Q.AND)
    if date_to_limit:
        date_filter_query.add(Q(orderproductlistitem__order__order_date__lte=date_to_limit), Q.AND)

    return date_filter_query


class APIQuery(graphene.ObjectType):
    all_categories = graphene.List(ProductCategoryType)
    category = graphene.Field(ProductCategoryType, id=graphene.ID(required=True))
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    top_sellers = graphene.List(ProductStatisticType, date_from=graphene.String(required=False), date_to=graphene.String(required=False))
    least_sellers = graphene.List(ProductStatisticType, date_from=graphene.String(required=False), date_to=graphene.String(required=False))
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID(required=True))

    def resolve_all_categories(self, info):
        return ProductCategory.objects.all()

    def resolve_category(self, info, id):
        try:
            return ProductCategory.objects.get(pk=id)
        except ProductCategory.DoesNotExist:
            return None

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_top_sellers(self, info, **kwargs):
        return Product.top_sellers(info.context.user, get_date_range_product_filter_from_kwargs(**kwargs))

    def resolve_least_sellers(self, info, **kwargs):
        return Product.least_sellers(info.context.user, get_date_range_product_filter_from_kwargs(**kwargs))

    def resolve_all_orders(self, info):
        return Order.objects.all()

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


schema = graphene.Schema(query=APIQuery)
