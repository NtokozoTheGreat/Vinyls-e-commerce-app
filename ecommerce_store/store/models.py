from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.


# catergory
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="uploads/category/", blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "catagories"


# customer
class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address1 = models.CharField(max_length=255, blank=True)
    address2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    province = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)
    zipcode = models.CharField(max_length=255, blank=True)
    old_cart = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


def create_customer_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = CustomerProfile(user=instance) 
        user_profile.save()


post_save.connect(create_customer_profile, sender=User)


# vendors
class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    store_name = models.CharField(max_length=100)
    store_description = models.TextField()
    phone_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=254, unique=True, blank=False)
    image = models.ImageField(upload_to="uploads/vendor/", blank=True, null=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    ratings_count = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.store_name


# products
class Product(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="products")
    vinyl_name = models.CharField(max_length=100)
    artist_name = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.TextField(default="", blank=True, null=True)
    track_list= models.TextField(default="", blank=True, null=True)
    image = models.ImageField(upload_to="uploads/product/", blank=True, null=True)
    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    ratings_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.vinyl_name} - {self.artist_name}"


class Ratings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ratings")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings", null=True, blank=True)
    score = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=120, blank=True)
    review = models.TextField(blank=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:

        verbose_name_plural = "ratings"

        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(vendor__isnull=False, product__isnull=True) |
                    models.Q(vendor__isnull=True, product__isnull=False)
                ),
                name="rating_exactly_one_target",
            ),
            models.UniqueConstraint(
                fields=["user", "vendor"],
                name="unique_user_vendor_rating",
                condition=models.Q(vendor__isnull=False),
            ),
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_rating",
                condition=models.Q(product__isnull=False),
            ),
        ]

    def __str__(self):
        target = self.vendor or self.product
        return f"{self.score} by {self.user.username} on {target}"

