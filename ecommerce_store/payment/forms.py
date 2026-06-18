from .models import ShippingAddress
from django import forms

class ShippingForm(forms.ModelForm):

    shipping_full_name = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}), required=True)
    shipping_email = forms.EmailField(label='', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}), required=True)
    shipping_address_1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address_1'}), required=True)
    shipping_address_2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address_2'}), required=False)
    shipping_city = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}), required=True)
    shipping_province = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Province'}), required=False)
    shipping_country = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}), required=True)
    shipping_zipcode = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Zipcode'}), required=False)

    class Meta:
        model = ShippingAddress
        fields = ['shipping_full_name', 'shipping_email',
                  'shipping_address_1', 'shipping_address_2',
                  'shipping_city', 'shipping_province',
                  'shipping_country', 'shipping_zipcode']

        exclude = ['user',]
