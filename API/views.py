from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.generics import ListAPIView
from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from API.api_permissions import AuthenticatedClientsOnly
from API.api_permissions import AuthenticatedSellersOnly
from API.models import Product
from API.models import Order
from API.models import Address
from API.models import DiscountCoupon
from API.serializers import ProductSerializer
from API.serializers import ProductManageSerializer
from API.serializers import ProductTopLeastSellersSerializer
from API.serializers import ProductTopLeastProfitableSerializer
from API.serializers import AddressSerializer
from API.serializers import OrderSerializer
from API.serializers import OrderCreateSerializer
from API.serializers import UserCreateSerializer
from API.serializers import DiscountCouponSerializer
from API.serializers import DiscountCouponCodesSerializer
from API.filters import ProductFilter
from API.filters import ProductTopSellersFilter
from API.filters import ProductLeastSellersFilter
from API.filters import ProductTopProfitableFilter
from API.filters import ProductLeastProfitableFilter


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


class ProductListCreateAPIView(ListCreateAPIView):
    serializer_class = ProductManageSerializer
    queryset = Product.objects.select_related('category').all().order_by('-pk')
    permission_classes = [AuthenticatedSellersOnly]


class ProductTopLeastBaseListAPIView(ListAPIView):
    serializer_class = ProductTopLeastSellersSerializer
    queryset = Product.objects.none()
    filterset_class = ProductTopSellersFilter
    permission_classes = [AuthenticatedSellersOnly]
    pagination_class = LimitOffsetPagination


class ProductTopSellersListAPIView(ProductTopLeastBaseListAPIView):
    def get_queryset(self):
        return Product.objects.top_sellers(self.request.user)


class ProductLeastSellersListAPIView(ProductTopLeastBaseListAPIView):
    filterset_class = ProductLeastSellersFilter

    def get_queryset(self):
        return Product.objects.least_sellers(self.request.user)


class ProductTopProfitableListAPIView(ProductTopLeastBaseListAPIView):
    serializer_class = ProductTopLeastProfitableSerializer
    filterset_class = ProductTopProfitableFilter

    def get_queryset(self):
        return Product.objects.most_profitable(self.request.user)


class ProductLeastProfitableListAPIView(ProductTopLeastBaseListAPIView):
    serializer_class = ProductTopLeastProfitableSerializer
    filterset_class = ProductLeastProfitableFilter

    def get_queryset(self):
        return Product.objects.most_profitable(self.request.user)


class AddressModelViewSet(ModelViewSet):
    serializer_class = AddressSerializer
    queryset = Address.objects.all()
    permission_classes = [AuthenticatedSellersOnly]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


class OrderModelViewSet(ModelViewSet):
    serializer_class = OrderCreateSerializer
    queryset = Order.objects.all()
    permission_classes = [AuthenticatedClientsOnly]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return OrderSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        q = Order.objects.none()

        if user.is_authenticated:
            if user.is_superuser:
                q = Order.objects.all().select_related('client').prefetch_related('orderproductlistitem_set')
            elif user.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists():
                q = Order.objects.filter(orderproductlistitem__product__seller=user)
            else:
                q = Order.objects.filter(client=user)

            return q.select_related('client').prefetch_related('orderproductlistitem_set').order_by("-pk")

        return q

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()
        client_email = instance.client.email
        payment_deadline = instance.payment_deadline.strftime("%m.%d.%Y, %H:%M:%S")

        send_mail(
            "Your order has been created",
            f"Thank you for shopping in our shop. \n"
            f"Make payment for your order ({instance.final_price} PLN) by {payment_deadline}.",
            settings.DEFAULT_EMAIL_ADDRESS,
            [client_email if client_email else "user.email@example.com"],
            fail_silently=True,
        )

        headers = self.get_success_headers(serializer.data)

        return Response({
            "total_product_price": instance.final_price,
            "payment_date": payment_deadline
        }, status=status.HTTP_201_CREATED, headers=headers)

    # add custom detail methods like 'pay_for_order', 'send_order', etc.


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
            "account_type": "Client" if instance.groups.filter(name=settings.USER_CLIENT_GROUP_NAME).exists() else "Seller"
        }, status=status.HTTP_201_CREATED, headers=headers)


class DiscountCouponModelViewSet(ModelViewSet):
    serializer_class = DiscountCouponSerializer
    queryset = DiscountCoupon.objects.all()
    permission_classes = [AuthenticatedClientsOnly]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return DiscountCoupon.objects.all()

        return DiscountCoupon.objects.none()

    @action(methods=['post'], detail=False, url_path='check-if-valid', url_name='api_coupons_validation_check')
    def check_if_valid(self, request):
        codes_serializer = DiscountCouponCodesSerializer(data=request.data)

        if codes_serializer.is_valid():
            codes = codes_serializer.validated_data['codes']
            validation = {c: {"valid": False, "discount": 0.0} for c in codes}
            current_time = timezone.now()
            coupons = DiscountCoupon.objects.filter(
                code__in=codes, is_used=False, is_expired=False, valid_date__gt=current_time
            )
            if coupons.exists():
                for coupon in coupons:
                    validation[coupon.code]["valid"] = True
                    validation[coupon.code]["discount"] = coupon.discount
                    validation[coupon.code]["id"] = coupon.pk

            return Response(validation, status=status.HTTP_200_OK)

        return Response(
            {'status': 'Empty data received! Provide at least one coupon code to check'},
            status=status.HTTP_400_BAD_REQUEST
        )
