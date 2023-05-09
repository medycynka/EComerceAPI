from django import template
from django.conf import settings
from django.template.defaultfilters import floatformat

import random


register = template.Library()


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
