from django.urls import path

from rest_framework.schemas import get_schema_view

import API.views as views

urlpatterns = [
    # API
    path('products/', views.ProductModelViewSet.as_view({'get': 'list'}), name='api_products_list'),
    path('products/list-create/', views.ProductListCreateAPIView.as_view(), name='api_products_list_create'),
    path('products/create/', views.ProductModelViewSet.as_view({
        'post': 'create',
    }), name='api_product_create'),
    path('products/manage/<pk>/', views.ProductModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='api_product_manage'),
    path('products/<pk>/', views.ProductModelViewSet.as_view({
        'get': 'retrieve',
    }), name='api_product_details'),
    path('top-sellers/', views.ProductTopSellersListAPIView.as_view(), name='api_products_top_sellers_list'),
    path('least-sellers/', views.ProductLeastSellersListAPIView.as_view(), name='api_products_least_sellers_list'),
    path('orders/', views.OrderListAPIView.as_view(), name='api_orders_list'),
    path('orders/create/', views.OrderCreateAPIView.as_view(), name='api_order_create'),
    path('users/create/', views.UserCreateAPIView.as_view(), name='api_user_create'),
    path('address/', views.AddressModelViewSet.as_view({'get': 'list'}), name='api_addresses_list'),
    path('address/create/', views.AddressModelViewSet.as_view({
        'post': 'create',
    }), name='api_address_create'),
    path('address/manage/<pk>/', views.AddressModelViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='api_address_manage'),
    path('address/<pk>/', views.AddressModelViewSet.as_view({
        'get': 'retrieve',
    }), name='api_address_detail'),
    # Schema
    path('openapi/', get_schema_view(
        title="E-commerce API",
        description="API for managing (creating, editing, deleting and retrieving) e-commerce models",
        version="1.0.0"
    ), name='api_openapi_schema'),
]
