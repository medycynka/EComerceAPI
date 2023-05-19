from django.urls import path, include

from rest_framework.schemas import get_schema_view
from rest_framework.routers import DefaultRouter

import API.views as views


api_router = DefaultRouter()
api_router.register(r'products', views.ProductModelViewSet, basename='api_products')
api_router.register(r'address', views.AddressModelViewSet, basename='api_address')
api_router.register(r'orders', views.OrderModelViewSet, basename='api_orders')
api_router.register(r'coupons', views.DiscountCouponModelViewSet, basename='api_coupons')

urlpatterns = [
    # API
    path('products/list-create/', views.ProductListCreateAPIView.as_view(), name='api_products_list_create'),
    path('top-sellers/', views.ProductTopSellersListAPIView.as_view(), name='api_products_top_sellers_list'),
    path('least-sellers/', views.ProductLeastSellersListAPIView.as_view(), name='api_products_least_sellers_list'),
    path('most-profitable/', views.ProductTopProfitableListAPIView.as_view(), name='api_products_most_profitable_list'),
    path('least-profitable/', views.ProductLeastProfitableListAPIView.as_view(), name='api_products_least_profitable_list'),
    path('users/create/', views.UserCreateAPIView.as_view(), name='api_user_create'),
    # Schema
    path('openapi/', get_schema_view(
        title="E-commerce API",
        description="API for managing (creating, editing, deleting and retrieving) e-commerce models",
        version="1.0.0"
    ), name='api_openapi_schema'),
    # Router
    path('', include(api_router.urls)),
]
