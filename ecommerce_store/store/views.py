from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import ProductForm, SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm, VendorProfileForm, RatingForm
from django.contrib.auth.decorators import login_required
from .models import Vendor, Product, Category, CustomerProfile
from django.db.models import Q, Avg, Count
import json
from cart.cart import Cart
from payment.forms import ShippingForm
from payment.models import ShippingAddress, OrderItem
from .models import Ratings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from django.core.mail import EmailMessage

# Create your views here.

"""
Views for the Vinyls marketplace application.

Provides functionality for:

- User registration and authentication
- Vendor registration and dashboard management
- Product and store browsing
- Product search and category browsing
- Customer profile management
- Product and vendor review system
- Rating aggregation and cache updates
"""


def home(request):
    """
    Display the marketplace homepage.

    Retrieves all available products and
    renders the main storefront.
    """
    products = Product.objects.all()
    
    return render(request, 'home.html', {'products': products})


def about_us(request):
    """
    Display the marketplace About Us page.
    """
    return render(request, 'aboutus.html', {})


def login_user(request):
    """
    Authenticate a user and restore their session.

    Customer shopping carts are restored from the
    stored CustomerProfile when available. Vendors
    are redirected to their dashboard after login.
    """
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        print("AUTH:", user)  # debug

        if user is not None:
            login(request, user)
            
            if hasattr(user, 'vendor'):
                messages.success(request, "You've logged in successfully.")
                return redirect('vendor_dashboard')
            
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
    """
    Register a new customer account.

    Creates a new user, authenticates them,
    and starts their first session.
    """
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


@login_required
def become_vendor(request):
    """
    Register the authenticated user as a vendor.

    Creates a storefront that allows the user
    to manage and sell products.
    """
    if hasattr(request.user, 'vendor'):
        messages.info(request, "You've already registered as a vendor.")
        return redirect('vendor_dashboard')

    if request.method == "POST":
        form = VendorProfileForm(request.POST, request.FILES)
        if form.is_valid():
            vendor = form.save(commit=False)
            vendor.user = request.user
            vendor.save()
            messages.success(request, f"Your store {vendor.store_name.title()} was successfully registered") 
            return redirect('vendor_dashboard')

        else:
            messages.error(request, 'There was an error registering your store. PLease check the form below.')
    else:
        form = VendorProfileForm()

    return render(request, "become_vendor.html", {'form': form})

@login_required
def add_product(request):
    """
    Create a new product listing.

    Only authenticated vendors or administrators
    are permitted to add products.
    """
    if not hasattr(request.user, "vendor") and not request.user.is_staff:
        messages.error(request, "Only vendors or admins can add products.")
        return redirect("home")

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.vendor = request.user.vendor
            product.save()
            messages.success(request, "Product added successfully")
            return redirect('vendor_dashboard')
        else:
            print(form.errors)
            messages.error(request, "There was an error adding your product...")
    else:
        form = ProductForm()

    return render(request, "add_product.html", {"form": form,
                                                "store": request.user.vendor,})


def vendor_dashboard(request):
    """
    Display the authenticated vendor dashboard.

    Shows the vendor's storefront information
    and all products they currently manage.
    """
    if not hasattr(request.user, 'vendor'):
        messages.error(request, "You don't have a vendor account.")
        return redirect('home')
    
    store = request.user.vendor
    products = store.products.all().order_by('-added_at')
    
    return render(request, "vendor_dashboard.html", {
        'store': store,
        'products': products,
    })


def product_detail(request, pk):
    """
    Display a product and its reviews.

    Determines whether the current user is
    eligible to submit a review based on
    completed purchases.
    """
    product = Product.objects.get(id=pk)
    tracklist = product.track_list.splitlines()
    reviews = product.ratings.select_related("user").order_by("-created_at")

    user_can_review = False
    already_reviewed = False

    if request.user.is_authenticated:
        user_can_review = OrderItem.objects.filter(
            order__customer=request.user,
            product=product,
            order__status="delivered",
        ).exists()

        already_reviewed = Ratings.objects.filter(
            user=request.user,
            product=product,
        ).exists()

    return render(request, "product.html", {
        "product": product,
        "reviews": reviews,
        "user_can_review": user_can_review,
        "already_reviewed": already_reviewed,
        "tracklist": tracklist,
    })


def store_detail(request, pk):
    """
    Display a vendor storefront.

    Shows store information, customer reviews,
    and determines whether the current user
    may submit a review.
    """
    stores = Vendor.objects.get(id=pk)
    description = stores.store_description
    reviews = stores.ratings.select_related("user").order_by("-created_at")
    
    user_can_review = False
    already_reviewed = False

    if request.user.is_authenticated:
        already_reviewed = reviews.filter(user=request.user).exists()
        user_can_review = not already_reviewed

    return render(request, "store.html", {   # <-- changed from "product.html"
        "stores": stores,
        "reviews": reviews,
        "user_can_review": user_can_review,
        "already_reviewed": already_reviewed,
        "description": description,
    })


def category(request, slug):
    """
    Display all products within a category.

    Retrieves the requested category using its
    slug and displays all associated products.
    """
    try:
        category = Category.objects.get(slug=slug)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
        
    except Category.DoesNotExist:
        messages.error(request, ("That category doesnt exist."))
        return redirect('home')
    
    
def genre_summary(request):
    """
    Display all available music genres.

    Used to help customers browse products
    by category.
    """
    categories = Category.objects.all()
    
    return render(request, 'genre_summary.html', {'categories': categories})


def record_collection_summary(request):
    """
    Display all available vinyl records.

    Lists every product currently available
    in the marketplace.
    """
    vinyls = Product.objects.all()

    return render(request, 'record_collection_summary.html', {'vinyls': vinyls})


def record_store_summary(request):
    """
    Display all registered record stores.

    Lists every vendor currently available
    on the marketplace.
    """
    stores = Vendor.objects.all()

    return render(request, 'record_store_summary.html', {'stores': stores})


def update_user(request):
    """
    Update the authenticated user's account information.

    Allows users to modify their profile
    details stored in the User model.
    """
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
    """
    Update the authenticated user's password.

    Re-authenticates the user after a
    successful password change.
    """
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
    """
    Update customer profile and shipping information.

    Saves both the customer profile and
    shipping address in a single request.
    """
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
    """
    Search products by vinyl title,
    artist name, or description.
    """

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


def popular_store(request):
    """
    Display vendors ordered by popularity.

    Stores are ranked using cached rating
    statistics.
    """

    stores = Vendor.objects.all().order_by('-ratings_count', '-average_rating')
    
    return render(request, 'popular_store.html', {'stores': stores})


def new_store(request):
    """
        Displays the most recently added stores.
    """
    stores = Vendor.objects.all().order_by('-added_at')

    return render(request, 'new_store.html', {'stores': stores})


def popular_vinyls(request):
    """
    Display products ranked by popularity.

    Products are ordered using their cached
    average rating and review count.
    """
    vinyls = Product.objects.all().order_by('-ratings_count', '-average_rating')
    return render(request, 'popular_vinyls.html', {'vinyls': vinyls})


def fresh_arrivals(request):
    """
    Display the most recently added products.
    """
    vinyls = Product.objects.all().order_by('-added_at')
    return render(request, 'fresh_arrivals.html', {'vinyls': vinyls})


@login_required
def rate_product(request, product_id):
    """
    Submit a review for a purchased product.

    Users may review a product only after
    their order has been delivered and may
    submit only one review per product.
    """
    product = get_object_or_404(Product, id=product_id)

    has_delivered_order = OrderItem.objects.filter(
        order__customer=request.user,
        product=product,
        order__status="delivered",
    ).exists()

    if not has_delivered_order:
        messages.error(request, "You can only review products after they've been delivered.")
        return redirect('productdetail', pk=product.id)

    already_reviewed = Ratings.objects.filter(user=request.user, product=product).exists()
    if already_reviewed:
        messages.error(request, "You've already reviewed this product.")
        return redirect('productdetail', pk=product.id)

    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.product = product
            rating.save()
            messages.success(request, "Your review has been uploaded")
            return redirect('productdetail', pk=product.id)
    else:
        form = RatingForm()

    return render(request, 'ratings.html', {"product": product, "form": form})

@login_required
def rate_vendor(request, vendor_id):
    """
    Submit a review for a vendor.

    Users may review a vendor only after
    completing a purchase from that store.
    """
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    has_delivered_order = OrderItem.objects.filter(
        order__customer=request.user,
        order__status="delivered",
        product__vendor=vendor,
    ).exists()
        
    if not has_delivered_order:
        messages.error(request, "You can only review stores after you've made a purchase.")
        return redirect('product_detail', pk=vendor.id)
    
    if request.method == "POST":
        form = RatingForm(request.POST)
        
        if form.is_valid():
            rating = form.save(commit=False)
            rating.user = request.user
            rating.vendor = vendor
            rating.save()
            messages.success(request, "Your review has been uploaded")
            return redirect('vendor_detail', pk=vendor.id)
    else:
        form = RatingForm()
    return render(request, 'ratings.html', {"vendor": vendor, "form": form})

@receiver([post_save, post_delete], sender=Ratings)
def update_rating_aggregates(sender, instance, **kwargs):
    """
    Maintain cached rating statistics.

    Recalculates the average rating and
    review count whenever a rating is
    created, updated, or deleted.
    """
    if instance.product:
        
        agg = instance.product.ratings.aggregate(avg=Avg("score"), count=Count("id"))
        instance.product.average_rating = agg["avg"] or 0
        instance.product.ratings_count = agg["count"]
        instance.product.save(update_fields=["average_rating", "ratings_count"])

    elif instance.vendor:
        
        agg = instance.vendor.ratings.aggregate(avg=Avg("score"), count=Count("id"))
        instance.vendor.average_rating = agg["avg"] or 0
        instance.vendor.ratings_count = agg["count"]
        instance.vendor.save(update_fields=["average_rating", "ratings_count"])
        
