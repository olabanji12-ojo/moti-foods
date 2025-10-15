from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import *
from django.db.models.signals import post_save, post_delete
from django.core.mail import send_mail, EmailMessage
from django.conf import settings


@receiver(user_logged_in)
def merge_cart_on_login(sender, request, user, **kwargs):
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return
    
    # Get or create an active order
    order, created = Order.objects.get_or_create(customer=user, complete=False)

    for pid, qty in session_cart.items():
        try:
            product = Product.objects.get(id=pid)
            item, created = OrderItem.objects.get_or_create(order=order, product=product)
            item.quantity = qty
            item.save()
        except Product.DoesNotExist:
            continue

    # Clear session cart after merging
    request.session['cart'] = {}
    request.session.modified = True



@receiver(post_save, sender=Payment)
def handle_successful_payment(sender, instance, created, **kwargs):
    """
    Automatically reset user's cart when a payment becomes successful.
    """
    # If payment is newly created or not yet successful, do nothing
    if instance.status != "success":
        return

    # Get the related order and user
    order = instance.order
    user = instance.customer

    print(f"✅ Payment verified successfully for user: {user}")
    print(f"🛒 Order ID: {order.id}")

    # Mark order as complete
    order.complete = True
    order.status = "processing"
    order.save()

    print("🔄 Order marked as complete.")

    # Delete all order items (reset cart)
    deleted_count, _ = OrderItem.objects.filter(order=order).delete()
    print(f"🗑️ Deleted {deleted_count} OrderItems for completed order.")

    # Create a new empty order for the user
    Order.objects.get_or_create(customer=user, complete=False)
    print("🆕 New empty order created for user.")

    print("🎉 Cart successfully reset after payment!\n")
    