from django.forms import ModelForm

from django_countries.widgets import CountrySelectWidget

from API.models import Address


class AddressForm(ModelForm):
    class Meta:
        model = Address
        fields = ("country", "city", "street", "street_number", "street_number_local", "post_code", "state")
        widgets = {"country": CountrySelectWidget()}
