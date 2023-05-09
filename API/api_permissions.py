from django.conf import settings

from rest_framework.permissions import BasePermission


class BaseAuthenticatedCustomUserGroupOnly(BasePermission):
    """
    Base class for checking if user has 'Client' or 'Seller' Permission
    """
    user_group_name = settings.USER_CLIENT_GROUP_NAME

    def has_permission(self, request, view):
        return request.user.is_authenticated and \
               (request.user.is_superuser or request.user.groups.filter(name=self.user_group_name).exists())


class AuthenticatedClientsOnly(BaseAuthenticatedCustomUserGroupOnly):
    """
    Allow only 'Clients'
    """
    pass


class AuthenticatedSellersOnly(BaseAuthenticatedCustomUserGroupOnly):
    """
    Allow only 'Sellers'
    """
    user_group_name = settings.USER_SELLER_GROUP_NAME
    
    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        return request.user.is_superuser or request.user == obj.seller
