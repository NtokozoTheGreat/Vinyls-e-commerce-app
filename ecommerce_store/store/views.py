from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from .forms import ProductForm, SignUpForm, VendorSignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django.contrib.auth.decorators import login_required
from .models import Vendor, Product, Category, CustomerProfile
from django.contrib.auth.forms import AuthenticationForm, forms
from django.db.models import Q
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress

# Create your views here.


def home(request):
    products = Product.objects.all()
    
    return render(request, 'home.html', {'products': products})


def about_us(request):
    return render(request, 'aboutus.html', {})


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        print("AUTH:", user)  # debug

        if user is not None:
            login(request, user)
            
            current_user = CustomerProfile.objects.get(user__id=request.user.id)
            
            saved_cart = current_user.old_cart
            
            if saved_cart:
                converted_cart = json.loads(saved_cart)
                
                cart = Cart(request)
                
                for key, value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)
                
            messages.success(request, ("Youve logged in successfully, please fill in billing info."))
            return redirect('update_info')

        else:
            messages.error(request, ("login unsuccessfull"))
            return redirect('login')

    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("you have been logged out..."))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            
            user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, (f"Youre successfully registered {username}"))
            return redirect('home')
        
        else:
            messages.error(request, ("there was an error registering you..."))
            return redirect('register')
        
    else:
        return render(request, "register.html", {'form': form})

def register_as_vendor(request):
    if request.method == "POST":
        form = VendorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']

            user = authenticate(request, username=username, password=password)
            if user is not None:

                login(request, user)
                messages.success(request, (f"Your store {form.cleaned_data['store_name'].title()} was successfully registered"))
                return redirect('vendor_dashboard')
            
            else:
                print(user)
                print(form.errors)  # debug
        
        else:
            messages.error(request, ("there was an error registering your store..."))
            return redirect('registervendor')
        
    else:
        form = VendorSignUpForm()
        return render(request, "registervendor.html", {'form': form})



@login_required
def add_product(request):
    if not hasattr(request.user, "vendor"):
        return redirect("home")  # only vendors allowed

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            return redirect("vendor_dashboard")
        else:
            messages.error(request, ("there was an error adding your product..."))
            return redirect('add_product')
    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form})


def vendor_dashboard(request):
    return render(request, "vendor_dashboard.html")


def product_detail(request, pk):
    product = Product.objects.get(id=pk)
    tracklist = product.track_list.splitlines()
    return render (request, "product.html", {"product": product, "tracklist": tracklist})

def category(request, slug):
    
    try:
        category = Category.objects.get(slug=slug)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
        
    except Category.DoesNotExist:
        messages.error(request, ("That category doesnt exist."))
        return redirect('home')
    
    
def genre_summary(request):
    
    categories = Category.objects.all()
    
    return render(request, 'genre_summary.html', {'categories': categories})


def record_collection_summary(request):

    vinyls = Product.objects.all()

    return render(request, 'record_collection_summary.html', {'vinyls': vinyls})


def store_detail(request, pk):
    store = Vendor.objects.get(id=pk)
    products = Product.objects.filter(vendor_id=pk)
    return render(request, "store_detail.html", {"store": store, "products": products})


def record_store_summary(request):

    stores = Vendor.objects.all()

    return render(request, 'record_store_summary.html', {'stores': stores})


def update_user(request):

    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)
       
        if user_form.is_valid():
            user_form.save()
            
            login(request, current_user)
            messages.success(request, "User has been updated")
            return redirect('home')
        return render(request, "update_user.html", {'user_form': user_form})
    
    else:
        messages.error(request, "you must be logged in")
        return redirect('home')

def update_password(request):

    if request.user.is_authenticated:
        current_user = request.user
        
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "password has been updated.")
                login(request, current_user)
                return redirect('home')

            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form':form})
    else:
        messages.error(request, "you must be logged in")
        return redirect('home')
    pass


def update_info(request):

    if request.user.is_authenticated:
        current_user = CustomerProfile.objects.get(user__id=request.user.id)
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_user, created = ShippingAddress.objects.get_or_create(user__id=request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()

            messages.success(request, "Your info has been updated")
            return redirect('home')
        return render(request, "update_info.html", {'form': form, 'shipping_form': shipping_form})

    else:
        messages.error(request, "you must be logged in")
        return redirect('home')


def search(request):

    if request.method == 'POST':
        searched = request.POST['searched']

        products = Product.objects.filter(Q(vinyl_name__icontains=searched) | Q(artist_name__icontains=searched) | Q(description__icontains=searched))

        if not searched:
            messages.success(request, "Product not found ")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {'searched': searched, 'products': products})
    else:
        return render(request, "search.html", {})
