from django.urls import path

import UserInterface.views as views

urlpatterns = [
    # Default Template views
    path('', views.HomeTemplateView.as_view(), name='home'),
    path('login/', views.LoginTemplateView.as_view(), name='login'),
    path('signup/', views.RegisterTemplateView.as_view(), name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('products/', views.ProductListTemplateView.as_view(), name='products_list'),
    path('products/create/', views.ProductCreateTemplateView.as_view(), name='product_create'),
    path('products/top-sellers/', views.ProductTopSellersListTemplateView.as_view(), name='products_top_sellers_list'),
    path('products/sells-stats/', views.ProductSellsStatsListTemplateView.as_view(), name='products_sells_statistics'),
    path('products/<pk>/', views.ProductDetailsTemplateView.as_view(), name='product_details'),
    path('orders/', views.OrdersListTemplateView.as_view(), name='orders_list'),
    path('orders/create/', views.OrderCreateTemplateView.as_view(), name='order_create'),
]
