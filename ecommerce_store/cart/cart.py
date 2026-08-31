from store.models import Product, CustomerProfile

class Cart():
    
    """
    Session-based shopping cart.

    The cart stores product IDs and quantities in the user's session.
    For authenticated users, the cart is also synchronized with the
    CustomerProfile model so it can be restored across sessions.
    """
    
    def __init__(self, request):
        """
        Session-based shopping cart.

        The cart stores product IDs and quantities in the user's session.
        For authenticated users, the cart is also synchronized with the
        CustomerProfile model so it can be restored across sessions.
        """
        self.session = request.session
        self.request = request

        cart = self.session.get('session_key')

        if "session_key" not in request.session:
            cart = self.session['session_key'] = {}

        self.cart = cart

    def db_add(self, product, quantity):
        """
        Add a product loaded from persistent storage to the session cart.

        This method is used when restoring a previously saved cart
        for an authenticated user.
        """
        product_id = str(product)
        product_qty = str(quantity)
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = CustomerProfile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")

            current_user.update(old_cart=str(carty))

    def add(self, product, quantity):
        """
        Add a product to the shopping cart.

        If the product already exists in the cart, no changes are made.
        Authenticated users have their cart synchronized with their
        CustomerProfile after the update.
        """
        product_id = str(product.id)
        product_qty = str(quantity)
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = CustomerProfile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")

            current_user.update(old_cart=str(carty))

    def __len__(self):
        return len(self.cart)

    def get_product(self):

        """
        Retrieve all Product objects currently stored
        in the shopping cart.
        """
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids)

        return products

    def get_quants(self):
        """
        Retrieve all Product objects currently stored
        in the shopping cart.
        """
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        """
        Update the quantity of an existing product in the cart.

        The updated cart is saved to the user's session and,
        for authenticated users, synchronized with their profile.
        """
        # product_id = self.cart.keys
        product_qty = int(quantity)
        product_id = str(product)

        ourcart = self.cart

        ourcart[product_id] = product_qty

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = CustomerProfile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")

            current_user.update(old_cart=str(carty))

        thing = self.cart

        return thing

    def delete(self, product):
        
        """
        Remove a product from the shopping cart.

        If the product exists, it is removed from both the session
        cart and the authenticated user's stored cart.
        """
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]

        self.session.modified = True

        if self.request.user.is_authenticated:
            current_user = CustomerProfile.objects.filter(user__id=self.request.user.id)
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")

            # Persist the current cart so authenticated users
            # can restore it in future sessions.
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        """
        Update the quantity of an existing product in the cart.

        The updated cart is saved to the user's session and,
        for authenticated users, synchronized with their profile.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        quantities = self.cart
        total = 0

        for key, value in quantities.items():
            key = int(key)
            for product in products:
                if product.id == key:
                    #if product.is_sale:
                    #total = total + (product.sale_price * value)
                    #else:
                        total = total + (product.price * value)

        return total
