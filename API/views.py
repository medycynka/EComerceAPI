from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.generics import CreateAPIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from API.api_permissions import AuthenticatedClientsOnly
from API.api_permissions import AuthenticatedSellersOnly
from API.models import ProductCategory
from API.models import Product
from API.models import Order
from API.models import Address
from API.models import DiscountCoupon
from API.serializers import ProductCategorySerializer
from API.serializers import ProductCategoryManageSerializer
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
from API.serializers import OrderStatusExtraExplanation
from API.filters import ProductFilter
from API.filters import ProductStatisticsFilter


class ProductCategoryModelViewSet(ModelViewSet):
    serializer_class = ProductCategoryManageSerializer
    queryset = ProductCategory.objects.root_nodes().prefetch_related('children')
    permission_classes = [IsAdminUser]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ProductCategorySerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]


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
    queryset = Product.objects.all().order_by('-pk')
    permission_classes = [AuthenticatedSellersOnly]


class ProductStatisticsListAPIView(mixins.ListModelMixin, GenericViewSet):
    serializer_class = ProductTopLeastSellersSerializer
    queryset = Product.objects.none()
    filterset_class = ProductStatisticsFilter
    permission_classes = [AuthenticatedSellersOnly]
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action in ['top_profitable', 'least_profitable']:
            return ProductTopLeastProfitableSerializer
        return self.serializer_class

    def get_queryset(self):
        if self.action == 'least_sellers':
            return Product.objects.least_sellers(self.request.user)
        elif self.action == 'top_profitable':
            return Product.objects.most_profitable(self.request.user)
        elif self.action == 'least_profitable':
            return Product.objects.least_profitable(self.request.user)
        return Product.objects.top_sellers(self.request.user)

    @action(methods=['get'], detail=False, url_path='top-sellers', url_name='top_sellers',
            name="Top selling products", description="List of products from least profitable to most")
    def top_sellers(self, request):
        return self.list(request)

    @action(methods=['get'], detail=False, url_path='least-sellers', url_name='least_sellers',
            name="Least selling products", description="List of products from least to most frequently purchased")
    def least_sellers(self, request):
        return self.list(request)

    @action(methods=['get'], detail=False, url_path='top-profitable', url_name='top_profitable',
            name="Top profitable products", description="List of products from most to least frequently purchased")
    def top_profitable(self, request):
        return self.list(request)

    @action(methods=['get'], detail=False, url_path='least-profitable', url_name='least_profitable',
            name="Least profitable products", description="List of products from least profitable to most")
    def least_profitable(self, request):
        return self.list(request)


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
        is_custom_action = self.action not in ['list', 'create', 'retrieve', 'update', 'partial_update', 'destroy']

        if is_custom_action:
            return OrderStatusExtraExplanation
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

    # add custom logic for actions, ex redirect to payment site after setting "PENDING_PAYMENT" status
    # region Order instance custom actions
    @action(methods=['post'], detail=True, url_path='payment-start', url_name='payment_start')
    def payment_start(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.PENDING_PAYMENT
        order.save()

        return Response({"action": "PENDING_PAYMENT", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='payment-success', url_name='payment_success')
    def payment_success(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.PAYMENT_RECEIVED
        order.is_paid = True
        order.save()

        return Response({"action": "PAYMENT_RECEIVED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='payment-failed', url_name='payment_failed')
    def payment_failed(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.FAILED
        order.save()

        return Response({"action": "FAILED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='confirm-order', url_name='confirm_order')
    def confirm_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.ORDER_CONFIRMED
        order.save()

        return Response({"action": "ORDER_CONFIRMED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='expire-order', url_name='expire_order')
    def expire_order(self, request, pk=None):
        order = self.get_object()
        if order.payment_deadline < timezone.now():
            order.status = Order.OrderStatus.EXPIRED
            order.save()

            return Response({"action": "EXPIRED", "status": "success"}, status=status.HTTP_200_OK)
        return Response(
            {"action": "EXPIRED", "status": "error", "msg": "The due date for this order has not yet passed!"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(methods=['post'], detail=True, url_path='awaiting-fulfillment', url_name='awaiting_fulfillment')
    def awaiting_fulfillment(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.AWAITING_FULFILLMENT
        order.save()

        return Response({"action": "AWAITING_FULFILLMENT", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='awaiting-shipment', url_name='awaiting_shipment')
    def awaiting_shipment(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.AWAITING_SHIPMENT
        order.save()

        return Response({"action": "AWAITING_SHIPMENT", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='hold-order', url_name='hold_order')
    def hold_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.ON_HOLD
        order.save()

        return Response({"action": "ON_HOLD", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='ship-order', url_name='ship_order')
    def ship_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.SHIPPED
        order.save()

        return Response({"action": "SHIPPED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='partial-ship-order', url_name='partial_ship_order')
    def partial_ship_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.PARTIALLY_SHIPPED
        order.save()

        return Response({"action": "PARTIALLY_SHIPPED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='wait-for-pickup', url_name='wait_for_pickup')
    def wait_for_pickup(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.AWAITING_PICKUP
        order.save()

        return Response({"action": "AWAITING_PICKUP", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='complete-order', url_name='complete_order')
    def complete_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.COMPLETED
        order.save()

        return Response({"action": "COMPLETED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='decline-order', url_name='decline_order')
    def decline_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.DECLINED
        order.save()

        return Response({"action": "DECLINED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='cancel-order', url_name='cancel_order')
    def cancel_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.CANCELED
        order.save()

        return Response({"action": "CANCELED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='refund-order', url_name='refund_order')
    def refund_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.REFUNDED
        order.save()

        return Response({"action": "REFUNDED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='partial-refund-order', url_name='partial_refund_order')
    def partial_refund_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.PARTIALLY_REFUNDED
        order.save()

        return Response({"action": "PARTIALLY_REFUNDED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='reject-refund', url_name='reject_refund')
    def reject_refund(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.REFUND_REJECTED
        order.save()

        return Response({"action": "REFUND_REJECTED", "status": "success"}, status=status.HTTP_200_OK)

    @action(methods=['post'], detail=True, url_path='dispute-order', url_name='dispute_order')
    def dispute_order(self, request, pk=None):
        order = self.get_object()
        order.status = Order.OrderStatus.DISPUTED
        order.save()

        return Response({"action": "DISPUTED", "status": "success"}, status=status.HTTP_200_OK)
    # endregion


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

    def get_serializer_class(self):
        if self.action == 'check_if_valid':
            return DiscountCouponCodesSerializer
        return self.serializer_class

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

            if codes_serializer.validated_data['flat']:
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
            else:
                validation = {c: {
                    "valid": False, "discount": 0.0, "invalid_reason": "Invalid coupon code."
                } for c in codes}
                current_time = timezone.now()
                coupons = DiscountCoupon.objects.filter(code__in=codes)

                if coupons.exists():
                    for coupon in coupons:
                        if coupon.is_used:
                            validation[coupon.code]["invalid_reason"] = "This coupon has already been used."
                        elif coupon.is_expired or coupon.valid_date < current_time:
                            validation[coupon.code]["invalid_reason"] = "This coupon is out of date."
                        else:
                            validation[coupon.code]["valid"] = True
                            validation[coupon.code]["discount"] = coupon.discount
                            validation[coupon.code]["invalid_reason"] = ""
                            validation[coupon.code]["id"] = coupon.pk

            return Response(validation, status=status.HTTP_200_OK)

        return Response(
            {'status': 'Empty data received! Provide at least one coupon code to check'},
            status=status.HTTP_400_BAD_REQUEST
        )
