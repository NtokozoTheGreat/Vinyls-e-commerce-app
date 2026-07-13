from django.shortcuts import render
from cart.cart import Cart
from .forms import ShippingForm, ShippingAddress, PaymentForm
from django.contrib import messages
from django.shortcuts import redirect
from payment.models import Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product
# Create your views here.


def payment_success(request):

    return render(request, 'payment/payment_success.html', {})


def checkout(request):

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
    
    if request.POST:
        payment_form = PaymentForm(request.POST or None)
        my_shipping = request.session.get("my_shipping")
        
        cart = Cart(request)
        cart_products = cart.get_product()
        quantities = cart.get_quants()
        totals = cart.cart_total()
        
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        shipping_address= f"{my_shipping['shipping_address_1']}\n{my_shipping['shipping_address_2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_province']}\n{my_shipping['shipping_country']}\n{my_shipping['shipping_zipcode']}"
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
        messages.success(request, 'Access denied' )
        return redirect('home')   

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_authenticated:
        orders = Order.objects.filter(status=("pending", "Pending"))
        return render(request, 'payment/not_shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, "Access denied")

    messages.success(request, "Order Placed")
    return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_authenticated:
        orders = Order.objects.filter(status=("shipped", "Shipped"))
        return render(request, 'payment/shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, "Access denied")
        
    messages.success(request, "Order Placed")
    return redirect('home')
