from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from API.api_permissions import AuthenticatedClientsOnly
from API.api_permissions import AuthenticatedSellersOnly
from API.models import Product
from API.models import Order
from API.serializers import ProductSerializer
from API.serializers import ProductManageSerializer
from API.serializers import ProductTopSellersSerializer
from API.serializers import OrderSerializer
from API.serializers import OrderCreateSerializer
from API.serializers import UserCreateSerializer
from API.filters import ProductFilter
from API.filters import ProductTopSellersFilter
from API.filters import ProductLeastSellersFilter


class ProductModelViewSet(ModelViewSet):
    serializer_class = ProductManageSerializer
    queryset = Product.objects.select_related('category').all().order_by('-pk')
    permission_classes = [AuthenticatedSellersOnly]
    filterset_class = ProductFilter

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


class ProductTopSellersListAPIView(ListAPIView):
    serializer_class = ProductTopSellersSerializer
    queryset = Product.objects.none()
    filterset_class = ProductTopSellersFilter
    permission_classes = [AuthenticatedSellersOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.top_sellers(self.request.user)


class ProductLeastSellersListAPIView(ListAPIView):
    serializer_class = ProductTopSellersSerializer
    queryset = Product.objects.none()
    filterset_class = ProductLeastSellersFilter
    permission_classes = [AuthenticatedSellersOnly]
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Product.least_sellers(self.request.user)


class OrderListAPIView(ListAPIView):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists():
                return Order.objects.all().order_by("-pk")
            return Order.objects.filter(client=user).order_by("-pk")
        return Order.objects.none()


class OrderCreateAPIView(CreateAPIView):
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()
    permission_classes = [AuthenticatedClientsOnly]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        client_email = instance.client.email
        payment_deadline = instance.payment_deadline.strftime("%m.%d.%Y, %H:%M:%S")

        send_mail(
            "Your order has been created",
            f"Thank you for shopping in our shop. \n"
            f"Make payment for your order ({instance.full_price} PLN) by {payment_deadline}.",
            settings.DEFAULT_EMAIL_ADDRESS,
            [client_email if client_email else "user.email@example.com"],
            fail_silently=True,
        )

        headers = self.get_success_headers(serializer.data)

        return Response({
            "total_product_price": instance.full_price,
            "payment_date": payment_deadline
        }, status=status.HTTP_201_CREATED, headers=headers)


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        headers = self.get_success_headers(serializer.data)

        return Response({
            "username": instance.username,
            "email": instance.email,
            "account_type": "Klient" if instance.groups.filter(name=settings.USER_CLIENT_GROUP_NAME).exists() else "Sprzedawca"
        }, status=status.HTTP_201_CREATED, headers=headers)

