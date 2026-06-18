from django.shortcuts import render
from cart.cart import Cart

# Create your views here.
def payment_success(request):

    return render(request, 'payment/payment_success.html', {})


def checkout(request):

    cart = Cart(request)
    cart_products = cart.get_product()
    quantities = cart.get_quants()
    totals = cart.cart_total()
    return render(request, 'payment/checkout.html', {"cart_products": cart_products,
                                                 "quantities": quantities,
                                                 "totals": totals}
                  )





