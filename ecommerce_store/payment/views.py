from django.shortcuts import render
from cart.cart import Cart
from .forms import ShippingForm, ShippingAddress, PaymentForm
from django.contrib import messages
from django.shortcuts import redirect, render
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
                                                 "shipping_form":shipping_}
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
        
        if request.user.is_authenticated:
            
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products,
                                                        "quantities": quantities,
                                                        "totals": totals,
                                                        "shipping_info":request.POST,
                                                        "billing_form":billing_form}
                            )
            
        else:

            shipping_info = request.POST
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products,
                                                            "quantities": quantities,
                                                            "totals": totals,
                                                            "shipping_info":shipping_info}
                            )
            
    else:
        messages.success(request, 'Access denied' )
        return redirect('home')