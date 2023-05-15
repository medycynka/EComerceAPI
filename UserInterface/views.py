from django.shortcuts import redirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth import logout
from django.conf import settings

from API.models import ProductCategory
from API.filters import ProductFilter


class RestrictAccessTemplateView(TemplateView):
    allowed_users_groups = None
    not_allowed_redirect = None

    def get(self, request, *args, **kwargs):
        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name=self.allowed_users_groups).exists():
                return super().get(request, *args, **kwargs)
            return redirect(self.not_allowed_redirect)

        return redirect('login')


class HomeTemplateView(TemplateView):
    template_name = 'basic.html'


class LoginTemplateView(TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        user = authenticate(request,
                            username=self.request.POST.get('username', None),
                            password=self.request.POST.get('pass', None)
                            )

        if user is not None:
            login(request, user)

            return redirect('home')
        else:
            context = self.get_context_data(**kwargs)
            context['errors'] = [
                'Błędna nazwa użytkownika lub hasło!'
            ]

            return render(request, self.template_name, context=context)


class RegisterTemplateView(TemplateView):
    template_name = 'register.html'


class ProductListTemplateView(TemplateView):
    template_name = 'products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        filter_class = ProductFilter()
        context['order_options'] = filter_class.filters['order'].field.choices
        context['category_options'] = ProductCategory.objects.all()

        return context


class ProductCreateTemplateView(RestrictAccessTemplateView):
    template_name = 'product_create.html'
    allowed_users_groups = settings.USER_SELLER_GROUP_NAME
    not_allowed_redirect = 'products_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = ProductCategory.objects.all()

        return context


class ProductDetailsTemplateView(TemplateView):
    template_name = 'product_details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['product_pk'] = kwargs.get('pk', None)

        user = self.request.user

        if user.is_authenticated:
            if user.is_superuser or user.groups.filter(name=settings.USER_SELLER_GROUP_NAME).exists():
                context['categories'] = ProductCategory.objects.all()

        return context


class ProductTopSellersListTemplateView(RestrictAccessTemplateView):
    template_name = 'top_sellers.html'
    allowed_users_groups = settings.USER_SELLER_GROUP_NAME
    not_allowed_redirect = 'home'


class ProductSellsStatsListTemplateView(RestrictAccessTemplateView):
    template_name = 'sells_statistics.html'
    allowed_users_groups = settings.USER_SELLER_GROUP_NAME
    not_allowed_redirect = 'home'


class OrderCreateTemplateView(RestrictAccessTemplateView):
    template_name = 'order_create.html'
    allowed_users_groups = settings.USER_CLIENT_GROUP_NAME
    not_allowed_redirect = 'home'


class OrdersListTemplateView(TemplateView):
    template_name = 'orders.html'


def user_logout(request):
    logout(request)

    return redirect('home')
