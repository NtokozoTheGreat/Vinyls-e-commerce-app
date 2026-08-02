from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms
from .models import Category, Product, Vendor, CustomerProfile, Ratings


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}))
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}))
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'

        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['password2'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'


class VendorProfileForm(forms.ModelForm):

    class Meta:
        model = Vendor
        fields = ['store_name', 'store_description', 'phone_number', 'email', 'image']
        widgets = {
            'store_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Store Name'}),
            'store_description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Store Description'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
        }
        
    def clean_email(self):
        email = self.cleaned_data['email']
        qs = Vendor.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A store with this email already exists.")
        return email



class UpdateUserForm(UserChangeForm):
    
    password = None
    
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Email Address'}),required=False)
    first_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'First Name'}),required=False)
    last_name = forms.CharField(label="", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Last Name'}),required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UpdateUserForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['placeholder'] = 'User Name'
        self.fields['username'].label = ''
        self.fields['username'].help_text = '<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>'
        
class ChangePasswordForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ['new_password1', 'new_password2']
        
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs['class'] = 'form-control'
        self.fields['new_password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = '<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>'

        self.fields['new_password2'].widget.attrs['class'] = 'form-control'
        self.fields['new_password2'].widget.attrs['placeholder'] = 'Confirm Password'
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>'
            

class ProductForm(forms.ModelForm):
    vinyl_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Vinyl Name'}))
    artist_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Artist Name'}))
    stock = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Stock'}))
    price = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Price'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Description'}))
    track_list = forms.CharField(required=False, widget=forms.Textarea(attrs={'class':'form-control', 'placeholder':'Track List'}))
    image = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class':'form-control'}))
    on_sale = forms.BooleanField(required=False)
    sale_price = forms.DecimalField(widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Sale Price'}), required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))

    class Meta:
        model = Product
        fields = [
            'vinyl_name', 'artist_name', 'stock', 'price',
            'category', 'description', 'track_list', 'image',
            'on_sale', 'sale_price'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        on_sale = cleaned_data.get('on_sale')
        sale_price = cleaned_data.get('sale_price')

        if on_sale and not sale_price:
            raise forms.ValidationError('Sale price is required when the product is on sale.')
        elif not on_sale:
            cleaned_data['sale_price'] = 0

        return cleaned_data


class UserInfoForm(forms.ModelForm):

    phone = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone'}), required=False)
    address1 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address1'}), required=False)
    address2 = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'address2'}), required=False)
    city = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'city'}), required=False)
    province = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'province'}), required=False)
    country = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'country'}), required=False)
    zipcode = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'zipcode'}), required=False)

    class Meta:
        model = CustomerProfile
        fields = ['phone', 'address1', 'address2', 'city', 'province', 'zipcode', 'country']


class RatingForm(forms.ModelForm):
    
    title = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'title'}), required=False)
    review = forms.CharField(label='', widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'review'}), required=False)

    class Meta:
        model = Ratings
        fields = ["score", "title", "review"]
        widgets = {
            "score": forms.RadioSelect(choices=[(i, i ) for i in range(1,6)])
        }

