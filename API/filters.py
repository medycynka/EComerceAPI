from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

import django_filters
from django_filters import rest_framework as filters

from API.models import ProductCategory
from API.models import Product


class ProductFilter(filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    category = django_filters.ModelChoiceFilter(queryset=ProductCategory.objects.all())
    description = django_filters.CharFilter(lookup_expr='icontains')
    price = django_filters.NumberFilter()
    price_range = django_filters.RangeFilter(field_name='price')
    order = django_filters.OrderingFilter(
        fields=(
            ('name', 'name'),
            ('category__name', 'category'),
            ('price', 'price'),
        ), field_labels={
            'category__name': 'Product category',
        }
    )
    seller = django_filters.ModelChoiceFilter(queryset=get_user_model().objects.all())

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'price_range', 'seller']


class ProductTopLeastSellersFilter(filters.FilterSet):
    date_from = django_filters.DateTimeFilter(label='From date limit')
    date_to = django_filters.DateTimeFilter(label='To date limit')

    def base_queryset(self, filter_q):
        raise NotImplementedError("Can't use query filtering on basic model!")

    class Meta:
        model = Product
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        self.form.fields['date_from'].input_formats = settings.DATETIME_INPUT_FORMATS
        self.form.fields['date_to'].input_formats = settings.DATETIME_INPUT_FORMATS

    def filter_queryset(self, queryset):
        date_from_limit = self.form.cleaned_data.get("date_from", None)
        date_to_limit = self.form.cleaned_data.get("date_to", None)

        date_filter_query = Q()

        if date_from_limit:
            date_filter_query.add(Q(orderproductlistitem__order__order_date__gte=date_from_limit), Q.AND)
        if date_to_limit:
            date_filter_query.add(Q(orderproductlistitem__order__order_date__lte=date_to_limit), Q.AND)

        if date_filter_query:
            queryset = self.base_queryset(date_filter_query)

        return queryset


class ProductTopSellersFilter(ProductTopLeastSellersFilter):
    def base_queryset(self, filter_q):
        return Product.objects.top_sellers(self.request.user, filter_q)


class ProductLeastSellersFilter(ProductTopLeastSellersFilter):
    def base_queryset(self, filter_q):
        return Product.objects.least_sellers(self.request.user, filter_q)


class ProductTopProfitableFilter(ProductTopLeastSellersFilter):
    def base_queryset(self, filter_q):
        return Product.objects.most_profitable(self.request.user, filter_q)


class ProductLeastProfitableFilter(ProductTopLeastSellersFilter):
    def base_queryset(self, filter_q):
        return Product.objects.least_profitable(self.request.user, filter_q)
