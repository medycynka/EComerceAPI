from django.contrib import admin

from API.models import ProductCategory
from API.models import Product
from API.models import Order
from API.models import OrderProductListItem

import random


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_filter = ('name',)
    search_fields = ('name',)


@admin.action(description='Randomise products categories')
def randomise_categories(modeladmin, request, queryset):
    products = Product.objects.all()
    categories = [category_id for category_id in ProductCategory.objects.all().values_list('id', flat=True)]

    for product in products:
        product.category_id = random.choice(categories)

    Product.objects.bulk_update(products, ['category'])


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'seller')
    list_filter = ('name', 'seller')
    search_fields = ('name', 'category__name')
    actions = [randomise_categories]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'order_address', 'order_date', 'payment_deadline', 'full_price', 'is_paid',)
    list_filter = ('client__email', 'order_date')
    search_fields = ('client__email',)


@admin.register(OrderProductListItem)
class OrderProductListItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity',)
    list_filter = ('product__name', 'quantity',)
    search_fields = ('product__name',)
