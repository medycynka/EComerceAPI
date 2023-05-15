from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings


class AdminAndSellerOnlyMixin(UserPassesTestMixin):
    permission_denied_message = "Only sellers can access this url!"

    def test_func(self):
        user = self.request.user
        if user.is_authenticated:
            return user.is_superuser or user.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists()
        return False

