from django.contrib import admin
from .models import Category, CustomerProfile, Vendor, Product, Ratings
from django.contrib.auth.models import User
from payment.models import Order, OrderItem
# Register your models here.

admin.site.register(Category)
admin.site.register(CustomerProfile)
admin.site.register(Vendor)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)


class ProfileInline(admin.StackedInline):
    model = CustomerProfile


class UserAdmin (admin.ModelAdmin):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]


admin.site.unregister(User)

admin.site.register(User, UserAdmin)


class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    model = Order
    inlines = [OrderItemInline]


admin.site.unregister(Order)

admin.site.register(Order, OrderAdmin)

class RatingAdmin(admin.ModelAdmin):
    model = Ratings
    fields = ["title", "score", "vendor", "product", "user", "review",]
    readonly_fields = ["created_at", "updated_at"]

admin.site.register(Ratings, RatingAdmin)
    
