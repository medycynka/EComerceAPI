from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.conf import settings

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from django_countries.serializer_fields import CountryField

from API.models import ProductCategory
from API.models import Product
from API.models import Address
from API.models import Order
from API.models import OrderProductListItem


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)


class UserCreateSerializer(ModelSerializer):
    account_type = serializers.ChoiceField(choices=(
        (settings.USER_CLIENT_GROUP_NAME, settings.USER_CLIENT_GROUP_NAME),
        (settings.USER_SELLER_GROUP_NAME, settings.USER_SELLER_GROUP_NAME),
    ), allow_blank=True, required=False)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'account_type']

    def create(self, validated_data):
        user_group_type = validated_data.pop('account_type', None)

        instance = self.Meta.model.objects.create_user(**validated_data)

        if instance.email is None or instance.email == '':
            instance.email = instance.username + "@email.com"

        user_group = Group.objects.get(name=user_group_type if user_group_type else settings.DEFAULT_USER_CUSTOM_GROUP)
        instance.groups.add(user_group)
        instance.save()

        return instance


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ProductSerializer(ModelSerializer):
    category = ProductCategorySerializer()
    seller = UserSerializer()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'seller')
        read_only_fields = ('id',)


class ProductManageSerializer(ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())
    seller = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'seller')
        read_only_fields = ['id', 'thumbnail', 'seller']


class ProductTopLeastSellersSerializer(ModelSerializer):
    category = ProductCategorySerializer()
    sells_count = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'sells_count')
        read_only_fields = ('id',)


class ProductTopLeastProfitableSerializer(ModelSerializer):
    category = ProductCategorySerializer()
    sells_count = serializers.IntegerField()
    total_profit = serializers.DecimalField(max_digits=18, decimal_places=2)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'category', 'photo', 'thumbnail', 'sells_count', 'total_profit')
        read_only_fields = ('id',)


class ProductListItemSerializer(ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderProductListItem
        fields = ('id', 'product', 'quantity')
        read_only_fields = ('id',)


class AddressSerializer(ModelSerializer):
    country = CountryField(country_dict=True)
    short_address = serializers.CharField(read_only=True)
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = Address
        fields = ('id', 'country', 'city', 'street', 'street_number', 'street_number_local', 'post_code', 'state',
                  'short_address', 'full_address')
        read_only_fields = ('id',)


class OrderSerializer(ModelSerializer):
    client = UserSerializer()
    order_address = AddressSerializer()
    products_list = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ('id', 'client', 'order_address', 'order_date', 'payment_deadline', 'full_price', 'status',
                  'products_list')
        read_only_fields = ('id',)

    def get_products_list(self, obj):
        return ProductListItemSerializer(obj.products_list, many=True).data


class OrderCreateSerializer(ModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    order_address = AddressSerializer()
    orderproductlistitem_set = ProductListItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ('client', 'order_address', 'orderproductlistitem_set')
        read_only_fields = ('id',)

    def create(self, validated_data):
        order_products = validated_data.pop('orderproductlistitem_set')
        address_data = validated_data.pop('order_address')
        order_address = Address.objects.create(**address_data)
        validated_data['order_address'] = order_address
        instance = super().create(validated_data)
        products_list = [
            OrderProductListItem(
                order=instance, product=item['product'], quantity=item['quantity']
            ) for item in order_products
        ]

        OrderProductListItem.objects.bulk_create(products_list)
        instance.save()

        return instance
