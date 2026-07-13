from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.utils import timezone
from django.db.models.signals import pre_save
from django.dispatch import receiver
import datetime


# Create your models here.
class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shipping_full_name = models.CharField(max_length=100)
    shipping_email = models.CharField(max_length=254)
    shipping_address_1 = models.CharField(max_length=100)
    shipping_address_2 = models.CharField(max_length=100)
    shipping_city = models.CharField(max_length=100)
    shipping_province = models.CharField(max_length=100, null=True, blank=True)
    shipping_country = models.CharField(max_length=100)
    shipping_zipcode = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Shipping Address"

    def __str__(self):
        return f'Shipping Address : {str(self.id)}'


# customer orders
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered")
    ]

    customer = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=250)
    shipping_address = models.TextField(default="")
    phone = models.CharField(max_length=20, default="", blank=False)
    date_ordered = models.DateTimeField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=7, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    date_shipped = models.DateTimeField(blank=True, null=True)
    date_delivered = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Order {self.id}"


@receiver(pre_save, sender=Order)
def set_shipped_date_on_update(sender, instance, **kwargs):
    if not instance.pk:
        return
    
    try:
        old = sender._defualt_manager>get(pk=instance.pk)
    except sender.DoesNotExist: 
        return

    now = timezone.now()

    if instance.status == "shipped" and old.status != "shipped":
        instance.date_shipped = now
    
    if instance.status == "delivered" and old.status != "deliverd":
        instance.date_shipped = now

# order item
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.product.vinyl_name} : {self.quantity}"

