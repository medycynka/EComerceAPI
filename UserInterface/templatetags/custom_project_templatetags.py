from django import template
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.defaultfilters import floatformat

from API.models import Product

import random
from typing import Union


register = template.Library()
USER_MODEL = get_user_model()


@register.filter(name="is_client")
def is_client(value):
    """
    Check if user is a `client`
    :param value: user model instance
    :return: Returns True if user is in "Clients" group
    """
    return value.is_authenticated and value.groups.filter(name=settings.USER_CLIENT_GROUP_NAME).exists()


@register.filter(name="is_seller")
def is_seller(value):
    """
    Check if user is a `seller`
    :param value: user model instance
    :return: Returns True if user is in "Sellers" group
    """
    return value.is_authenticated and value.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists()


@register.simple_tag(name='random_int')
def random_int(start, stop=None, format_value=False):
    if stop is None:
        start, stop = 0, stop

    return floatformat(random.randint(start, stop), "2g") if format_value else random.randint(start, stop)


@register.filter(name="can_see_product_stats")
def can_see_product_stats(user: USER_MODEL, product_id: Union[int, str]):
    """
    Check if user can see detailed product statistics (is admin or passed product seller)
    :param user: user model instance
    :param product_id: id of product instance
    :return: True user can see detailed product statistics
    """
    if user.is_authenticated:
        return user.is_superuser or Product.objects.filter(pk=product_id, seller=user).exists()
    return False
