from django.urls import path

import API.views as views

urlpatterns = [
    # API
    path('products/', views.ProductModelViewSet.as_view({'get': 'list'}), name='api_products_list'),
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
]
