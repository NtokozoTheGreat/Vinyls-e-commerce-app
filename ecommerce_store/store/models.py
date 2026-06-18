from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
from django.db.models.signals import post_save
# Create your models here.


# catergory
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

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

    def __str__(self):
        return f"{self.vinyl_name} - {self.artist_name}"
