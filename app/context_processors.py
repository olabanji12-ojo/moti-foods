from .models import Order, OrderItem, Product

def cart_item_count(request):
    if request.user.is_authenticated:
        # Get the active order for logged-in users
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        count = order.get_cart_items
    else:
        # Get cart from session for guests
        cart = request.session.get('cart', {})
        count = sum(cart.values())

    return {
        'cart_items_count': count
    }
