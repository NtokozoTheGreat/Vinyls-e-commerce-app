from django.shortcuts import render
from cart.cart import Cart
from .forms import ShippingForm, ShippingAddress, PaymentForm
from django.contrib import messages
from django.shortcuts import redirect
from payment.models import Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product
from django.utils import timezone
from store.models import CustomerProfile
# Create your views here.

"""
Views responsible for the checkout and order workflow.

Provides functionality for checkout, billing,
order creation, payment confirmation,
and order management for administrators.
"""


def payment_success(request):
    """
    Display the payment confirmation page after a
    successful order.
    """

    return render(request, 'payment/payment_success.html', {})


def checkout(request):
    """
    Display the checkout page.

    Loads the current shopping cart and pre-populates
    the shipping form for authenticated users.
    """

    cart = Cart(request)
    cart_products = cart.get_product()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(user=request.user)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        except ShippingAddress.DoesNotExist:
            shipping_form = ShippingForm(request.POST or None)

        return render(request, 'payment/checkout.html', {"cart_products": cart_products,
                                                 "quantities": quantities,
                                                 "totals": totals,
                                                 "shipping_form":shipping_form}
                      )

    else:
        shipping_form = ShippingForm(request.POST or None)
        
        return render(request, 'payment/checkout.html', {"cart_products": cart_products,
                                                 "quantities": quantities,
                                                 "totals": totals,
                                                 "shipping_form":shipping_form}
                      )


def cart_summary(request):
    return render(request, 'cart_summary.html')


def billing_info(request):
    """
    Collect billing information before an order
    is processed.

    Shipping details are temporarily stored in the
    user's session for use during checkout.
    """
    
    if request.POST:
    
        cart = Cart(request)
        cart_products = cart.get_product()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        
        if request.user.is_authenticated:
            
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products,
                                                        "quantities": quantities,
                                                        "totals": totals,
                                                        "shipping_info":request.POST,
                                                        "billing_form":billing_form}
                            )
            
        else:
            billing_form = PaymentForm()
            shipping_info = request.POST
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products,
                                                            "quantities": quantities,
                                                            "totals": totals,
                                                            "shipping_info":shipping_info,
                                                            "billing_form":billing_form}
                            )
            
    else:
        messages.success(request, 'Access denied' )
        return redirect('home')


def process_order(request):
    """
    Create an order from the current shopping cart.

    Creates the order record, stores each purchased
    item, clears the user's cart, and redirects
    to the home page after completion.
    """
    
    if request.POST:
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get("my_shipping")
        
        cart = Cart(request)
        cart_products = cart.get_product()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address = f"{my_shipping['shipping_address_1']}\n{my_shipping['shipping_address_2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_province']}\n{my_shipping['shipping_country']}\n{my_shipping['shipping_zipcode']}"
        amount_paid = totals

        if request.user.is_authenticated:
            user = request.user
            
            create_order = Order(customer=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.on_sale:
                    price = product.sale_price
                else:
                    price = product.price
                    
                for key,value in quantities.items():
                    if int(key) == product_id:
                        create_order_item = OrderItem(user=user, order=create_order, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
                    
            for key in list(request.session.keys()):
                if key == "session_key":
                    
                    del request.session[key]
                
                current_user = CustomerProfile.objects.filter(user__id=request.user.id)
                current_user.update(old_cart="")
                
            messages.success(request, "Order Placed")
            return redirect('home')
            
        else:
            create_order = Order(full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()
            
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                if product.on_sale:
                    price = product.sale_price
                else:
                    price = product.price
                    
                for key,value in quantities.items():
                    if int(key) == product_id:
                        create_order_item = OrderItem(order=create_order, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()
                    
                for key in list(request.session.keys()):
                    if key == "session_key":
                    
                        del request.session[key]
            
            messages.success(request, "Order Placed")
            return redirect('home')
            
    else:
        messages.success(request, 'Access denied')
        return redirect('home')


def not_shipped_dash(request):
    """
    Display all pending orders.

    Administrators can update the status of
    orders awaiting shipment.
    """
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Access denied")
        return redirect('home')

    orders = Order.objects.filter(status="pending")

    if request.method == "POST":
        new_status = request.POST.get('shipping_status')
        num = request.POST.get('num')

        if not num:
            messages.error(request, "No order specified")
            return redirect("not_shipped_dash")

        try:
            order = Order.objects.get(id=num)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect("not_shipped_dash")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == "shipped" and not order.date_shipped:
                order.date_shipped = timezone.now()
            elif new_status == "delivered" and not order.date_delivered:
                order.date_delivered = timezone.now()
            order.save()
            messages.success(request, "Shipping status updated")
        else:
            messages.error(request, "Invalid status")

        return redirect("not_shipped_dash")

    return render(request, 'payment/not_shipped_dash.html', {'orders': orders})


def shipped_dash(request):
    """
    Display all shipped orders.

    Administrators can update the status of
    orders that are currently in transit.
    """
    if not (request.user.is_authenticated and request.user.is_superuser):
        messages.error(request, "Access denied")
        return redirect('home')

    orders = Order.objects.filter(status="shipped")

    if request.method == "POST":
        new_status = request.POST.get('shipping_status')
        num = request.POST.get('num')

        if not num:
            messages.error(request, "No order specified")
            return redirect("shipped_dash")

        try:
            order = Order.objects.get(id=num)
        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect("shipped_dash")

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == "shipped" and not order.date_shipped:
                order.date_shipped = timezone.now()
            elif new_status == "delivered" and not order.date_delivered:
                order.date_delivered = timezone.now()
            order.save()
            messages.success(request, "Shipping status updated")
        else:
            messages.error(request, "Invalid status")

        return redirect("home")

    return render(request, 'payment/shipped_dash.html', {'orders': orders})

def orders(request, pk):
    """
    Display the details of an individual order.

    Administrators can review purchased items
    and update the order status.
    """
    if not (request.user.is_authenticated and request.user.is_superuser):
        return redirect("home")

    order = Order.objects.get(id=pk)
    order_items = OrderItem.objects.filter(order=pk)

    if request.method == "POST":
        new_status = request.POST.get('shipping_status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            if new_status == "shipped" and not order.date_shipped:
                order.date_shipped = timezone.now()
            elif new_status == "delivered" and not order.date_delivered:
                order.date_delivered = timezone.now()
            order.save()
            messages.success(request, "Shipping status updated")
        else:
            messages.error(request, "Invalid status")

        return redirect("home")

    return render(request, 'payment/orders.html', {
        "order": order,
        "order_items": order_items,
    })
