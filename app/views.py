from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import * 
from .forms import CustomerCreationForm

from django.http import JsonResponse, HttpResponse
import json
from decimal import Decimal

import uuid
from django.urls import reverse
from .paystack import  paystack_checkout, verify_payment

import hmac
import hashlib



# Create your views here.

def welcome(request):
    # Get the "Zobo" category
    drinks_category = Category.objects.get(name='Zobo')
    # Get the first product under Zobo
    first_drink = drinks_category.products.first()

    # Get the "Banana Bread" category
    breads_category = Category.objects.get(name='Banana Bread')
    # Get the first product under Banana Bread
    first_bread = breads_category.products.first()

    context = {
        'first_drink': first_drink,
        'first_bread': first_bread,
    }
    return render(request, 'welcome.html', context)


def product_page(request):
    drinks = Category.objects.get(name='Zobo')
    breads = Category.objects.get(name='Banana Bread')
    product1 = drinks.products.all()
    product2 = breads.products.all()

    reviews = Review.objects.all()[:5]

    if request.method == 'POST':
        rating = request.POST.get('rating')
        message = request.POST.get('message')

        if rating and message:
            # Get or create customer
            if request.user.is_authenticated:
                customer, created = Customer.objects.get_or_create(name=request.user)
            else:
                customer = None
            
            Review.objects.create(
                customer=customer,
                rating=int(rating),
                message=message
            )
            messages.success(request, 'Thank you for your review!')
            return redirect('product_page')
        else:
            messages.error(request, 'Please provide both rating and review text.')


    context = {'product1': product1, 'product2': product2, 'reviews':reviews}
    return render(request, 'buyers/product_page.html', context)


def product_id(request, id):
    product = Product.objects.get(id=id)
    context = {'product': product}
    return render(request, 'buyers/product_id.html', context)

def cart(request):
    # --- Logged-in user ---
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.items.all()

        cart_total = float(order.get_cart_total)
        cart_items_count = (order.get_cart_items)

        # Format items into a consistent structure
        formatted_items = []
        for item in items:
            formatted_items.append({
                'id': item.id,
                'product': item.product,
                'quantity': (item.quantity),
                'get_total': float(item.get_total),
            })

    # --- Guest user ---
    else:
        cart = request.session.get('cart', {})
        formatted_items = []
        cart_total = 0
        cart_items_count = sum(cart.values())

        for pid, qty in cart.items():
            try:
                product = Product.objects.get(id=pid)
                total = product.price * qty
                cart_total += total
                formatted_items.append({
                    'id': pid,  # use product id as fallback
                    'product': product,
                    'quantity': qty,
                    'get_total': total
                })
            except Product.DoesNotExist:
                continue

    context = {
        'cart_items': formatted_items,
        'cart_total': cart_total,
        'cart_items_count': cart_items_count,
    }
    return render(request, 'buyers/cart.html', context)


def checkout(request):
    # --- Logged-in user ---
    if request.user.is_authenticated:
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        items = order.items.all()
        
        # Format items consistently
        cart_items = []
        for item in items:
            cart_items.append({
                'product': item.product,
                'quantity': item.quantity,
                'get_total': item.get_total,
            })

        # Auto-fill user info
        user_info = {
            'name': request.user.get_full_name(),
            'email': request.user.email
        }

        cart_total = order.get_cart_total

    # --- Guest user ---
    else:
        cart = request.session.get('cart', {})
        cart_items = []
        cart_total = 0

        for pid, qty in cart.items():
            try:
                product = Product.objects.get(id=pid)
                total = product.price * qty
                cart_total += total
                cart_items.append({
                    'product': product,
                    'quantity': qty,
                    'get_total': total,
                })
            except Product.DoesNotExist:
                continue

        user_info = {
            'name': '',
            'email': ''
        }

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'user_info': user_info,
    }
    return render(request, 'buyers/checkout.html', context)


def login_page(request):

    if request.user.is_authenticated:
        return redirect('product_page')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
       
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('product_page')
        else:
            messages.error(request, 'Invalid email or password')


    context = {}
    return render(request, 'login_page.html', context)

def register_page(request):
    
    form = CustomerCreationForm()
    
    if request.method == 'POST':
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login_page')
    context = {'form':form}
    return render(request, 'register_page.html', context)

def logout_page(request):

    logout(request)
    return redirect('login_page')


def update_cart(request):
    data = json.loads(request.body)
    product_id = data['product_id']
    action = data['action']

    # --- Logged-in user ---
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            order_item.quantity += 1
        elif action == 'remove':
            order_item.quantity -= 1
        elif action == 'delete':
            order_item.quantity = 0

        if order_item.quantity <= 0:
            order_item.delete()
            quantity = 0
            item_total = 0
        else:
            order_item.save()
            quantity = order_item.quantity
            item_total = order_item.get_total

        return JsonResponse({
            'quantity': (quantity),
            'item_total': float(item_total),
            'cart_total': float(order.get_cart_total),
            'cart_items': (order.get_cart_items),
            'cart_count': (order.get_cart_items),   # keep consistent with JS
        })

    # --- Guest user ---
    else:
        cart = request.session.get('cart', {})
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        if action == 'add':
            cart[product_id] = cart.get(product_id, 0) + 1
        elif action == 'remove':
            if product_id in cart:
                cart[product_id] -= 1
                if cart[product_id] <= 0:
                    del cart[product_id]
        elif action == 'delete':
            if product_id in cart:
                del cart[product_id]

        request.session['cart'] = cart

        # safer recompute totals
        quantity = cart.get(product_id, 0)
        item_total = float(product.price) * quantity if quantity > 0 else 0

        cart_total = 0
        cart_items_count = 0
        for pid, qty in cart.items():
            try:
                prod = Product.objects.get(id=pid)
                cart_total += float(prod.price) * qty
                cart_items_count += qty
            except Product.DoesNotExist:
                continue

        return JsonResponse({
            'quantity': (quantity),
            'item_total': float(item_total),
            'cart_total': float(cart_total),
            'cart_items': (cart_items_count),
            'cart_count': (cart_items_count),   # same as above
        })

    data = json.loads(request.body)
    product_id = data['product_id']
    action = data['action']

    # --- Logged-in user ---
    if request.user.is_authenticated:
        product = Product.objects.get(id=product_id)
        order, created = Order.objects.get_or_create(customer=request.user, complete=False)
        order_item, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            order_item.quantity += 1
        elif action == 'remove':
            order_item.quantity -= 1
        elif action == 'delete':
            order_item.quantity = 0

        if order_item.quantity <= 0:
            order_item.delete()
            quantity = 0
            item_total = 0
        else:
            order_item.save()
            quantity = order_item.quantity
            item_total = order_item.get_total

        return JsonResponse({
            'quantity': (quantity),
            'item_total': float(item_total),
            'cart_total': float(order.get_cart_total),
            'cart_items': (order.get_cart_items),
            'cart_count': (order.get_cart_items),

        })

    # --- Guest user ---
    else:
        cart = request.session.get('cart', {})
        product = Product.objects.get(id=product_id)

        if action == 'add':
            cart[product_id] = cart.get(product_id, 0) + 1
        elif action == 'remove':
            if product_id in cart:
                cart[product_id] -= 1
                if cart[product_id] <= 0:
                    del cart[product_id]
        elif action == 'delete':
            if product_id in cart:
                del cart[product_id]

        request.session['cart'] = cart

        # recompute totals
        quantity = cart.get(product_id, 0)
        item_total = product.price * quantity if quantity > 0 else 0
        cart_total = sum(Product.objects.get(id=pid).price * qty for pid, qty in cart.items())
        cart_items_count = sum(cart.values())

        return JsonResponse({
            'quantity': (quantity),
            'item_total': float(item_total),
            'cart_total': float(cart_total),
            'cart_items': float(cart_items_count),
            'cart_count': (order.get_cart_items),
        })


@login_required
def create_paystack_checkout_session(request):
    """
    Creates a Paystack checkout session for the current user's cart.
    """
    # 1️⃣ Get the current order
    try:
        order = Order.objects.get(customer=request.user, complete=False)
    except Order.DoesNotExist:
        messages.error(request, "Your cart is empty!")
        return redirect("cart")
    
    if order.get_cart_items == 0:
        messages.error(request, "Your cart is empty!")
        return redirect("cart")
    
    # 2️⃣ Create or get existing payment for this order
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            "customer": request.user,
            "reference": f"ORDER-{order.id}-{uuid.uuid4().hex[:8].upper()}",
            "amount": order.get_cart_total,
            "status": "pending",
        },
    )

    # 3️⃣ Prepare callback URL
    payment_success_url = reverse("payment-success")
    callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

    # 4️⃣ Prepare Paystack data
    checkout_data = {
        "email": request.user.email,
        "amount": int(order.get_cart_total * 100),  # Convert to kobo
        "currency": "NGN",
        "reference": payment.reference,  # ✅ Use saved reference
        "callback_url": callback_url,
        "metadata": {
            "order_id": order.id,
            "user_id": request.user.id,
            "customer_name": request.user.name,
        },
    }

    # 5️⃣ Initialize checkout
    status, checkout_url_or_error = paystack_checkout(checkout_data)

    if status:
        return redirect(checkout_url_or_error)
    else:
        messages.error(request, checkout_url_or_error)
        return redirect("checkout")

# Payment Success view Page
@login_required
def payment_success(request):
    """
    Handle successful Paystack payment.
    """
    reference = request.GET.get("reference")

    if not reference:
        messages.error(request, "No payment reference provided.")
        return redirect("cart")

    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        messages.error(request, "Payment record not found.")
        return redirect("cart")

    # Verify payment with Paystack
    if not verify_payment(reference):
        messages.error(request, "Payment verification failed.")
        return redirect("cart")

    # Mark order as complete
    order = payment.order
    order.complete = True
    order.status = "processing"
    order.save()

    # Update payment status
    payment.status = "success"
    payment.save()

    # Clear OrderItems
    order.items.all().delete()

    # Clear session cart (guest users)
    if "cart" in request.session:
        del request.session["cart"]
        request.session.modified = True

    # Create new empty order for the user
    Order.objects.get_or_create(customer=request.user, complete=False)

    messages.success(request, "Payment successful! Your order is being processed.")
    return render(request, "buyers/payment_success.html", {"payment": payment})


@login_required
def initiate_payment(request):
    """
    Handles checkout form submission and redirects to Paystack.
    """
    if request.method != "POST":
        return redirect("checkout")

    # Debug: Print all POST data
    print("=== PAYMENT INITIATION DEBUG ===")
    print(f"POST data: {dict(request.POST)}")
    
    # Get current order
    try:
        order = Order.objects.get(customer=request.user, complete=False)
    except Order.DoesNotExist:
        messages.error(request, "Your cart is empty!")
        return redirect("cart")

    if order.get_cart_items == 0:
        messages.error(request, "Your cart is empty!")
        return redirect("cart")

    # Save shipping info
    ShippingAddress.objects.create(
        customer=request.user,
        order=order,
        address=request.POST.get("address"),
        city=request.POST.get("city"),
        state=request.POST.get("state"),
        zipcode=request.POST.get("zipcode"),
        phone_number=request.POST.get("phone"),
    )

    # ✅ FIXED: Always generate a NEW reference for each payment attempt
    new_reference = f"ORDER-{order.id}-{uuid.uuid4().hex[:8].upper()}"
    
    # Get or create payment with NEW reference
    payment, created = Payment.objects.get_or_create(
        order=order,
        status="pending",  # Only get pending payments
        defaults={
            "customer": request.user,
            "reference": new_reference,
            "amount": order.get_cart_total,
        },
    )
    
    # If payment already exists but is pending, update with new reference
    if not created:
        payment.reference = new_reference
        payment.amount = order.get_cart_total
        payment.save()

    # Callback URL
    payment_success_url = reverse("payment-success")
    callback_url = f"{request.scheme}://{request.get_host()}{payment_success_url}"

    # Prepare Paystack data
    checkout_data = {
        "email": request.POST.get("email"),
        "amount": int(order.get_cart_total * 100),
        "currency": "NGN",
        "reference": payment.reference,  # Use the new reference
        "callback_url": callback_url,
        "metadata": {
            "order_id": order.id,
            "user_id": request.user.id,
            "customer_name": request.POST.get("fullName"),  # ✅ Changed from 'name' to 'fullName'
        },
    }

    # Debug: Print checkout data
    print(f"Checkout data: {checkout_data}")
    print(f"Order total: {order.get_cart_total}")

    # Initialize Paystack
    status, checkout_url_or_error = paystack_checkout(checkout_data)  # or checkout() depending on your function name

    # Debug: Print Paystack response
    print(f"Paystack status: {status}")
    print(f"Paystack response: {checkout_url_or_error}")
    
    if status:
        print(f"Redirecting to: {checkout_url_or_error}")
        return redirect(checkout_url_or_error)
    else:
        print(f"Paystack error: {checkout_url_or_error}")
        messages.error(request, f"Payment initialization failed: {checkout_url_or_error}")
        return redirect("checkout")


def paystack_webhook(request):
    # Get Paystack's secret key
    secret = settings.PAYSTACK_SECRET_KEY
    
    # Get the raw request body (the data Paystack sent)
    request_body = request.body
    
    # Create a hash using our secret key
    # This proves the request really came from Paystack
    hash_object = hmac.new(
        secret.encode('utf-8'), 
        request_body, 
        hashlib.sha512
    )
    computed_hash = hash_object.hexdigest()
    
    # Get the signature Paystack sent in the header
    paystack_signature = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    
    # Compare the two hashes - if they match, request is genuine
    if computed_hash == paystack_signature:
        # Convert JSON to Python dictionary
        webhook_data = json.loads(request_body)
        
        # Check if this is a successful charge
        if webhook_data.get("event") == "charge.success":
            # Get the payment reference
            reference = webhook_data["data"]["reference"]
            
            # Find the payment in our database
            try:
                payment = Payment.objects.get(reference=reference)
                
                # Update payment status to success
                payment.status = "success"
                payment.save()
                
                print(f"✅ Payment {reference} marked as successful via webhook")
                
            except Payment.DoesNotExist:
                print(f"⚠️ Payment with reference {reference} not found")
    
    # Always return 200 to tell Paystack we received the webhook
    return HttpResponse(status=200)
