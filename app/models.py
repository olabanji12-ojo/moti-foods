from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import Decimal


# --------------------
# CATEGORY
# --------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

        
# -------------------- 
# PRODUCT
# --------------------
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField(blank=True)
    product_image = models.ImageField(upload_to="")
    stock = models.PositiveIntegerField(default=0)
    available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.category.name} - {self.name}"


# --------------------
# CUSTOMER (Custom User)
# --------------------
class Customer(AbstractUser):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'name']

    def __str__(self):
        return self.email


# --------------------
# ORDER
# --------------------
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.customer}"

    @property
    def get_cart_total(self):
        total = sum(item.get_total for item in self.items.all())
        return Decimal(total)

    @property
    def get_cart_items(self):
        return sum(item.quantity for item in self.items.all())


# --------------------
# ORDER ITEM
# --------------------
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return self.product.price * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# --------------------
# SHIPPING ADDRESS
# --------------------
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=15)
    date_added = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        return f"{self.address}, {self.city}"


class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    message = models.TextField(null=True, blank=True, max_length=200)
    rating = models.IntegerField(default=5, choices=[(i, i) for i in range(1, 6)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.customer.name if self.customer else 'Anonymous'} - {self.rating}★"

    def time_since(self):
        """Returns human-readable time like '2 days ago'"""
        from django.utils import timezone
        diff = timezone.now() - self.created
        
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "Just now"
        elif seconds < 3600:  # Less than 1 hour
            minutes = int(seconds / 60)
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        elif seconds < 86400:  # Less than 1 day
            hours = int(seconds / 3600)
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif seconds < 604800:  # Less than 1 week
            days = int(seconds / 86400)
            if days == 1:
                return "Yesterday"
            return f"{days} days ago"
        elif seconds < 2592000:  # Less than 30 days
            weeks = int(seconds / 604800)
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif seconds < 31536000:  # Less than 1 year
            months = int(seconds / 2592000)
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = int(seconds / 31536000)
            return f"{years} year{'s' if years > 1 else ''} ago"
            

# --------------------
# PAYMENT
# --------------------
class Payment(models.Model):
    PAYMENT_STATUS = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    reference = models.CharField(max_length=100, unique=True)  # Paystack reference
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    access_code = models.CharField(max_length=100, blank=True, null=True)
    transaction_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-transaction_date']

    def __str__(self):
        return f"Payment {self.reference} - {self.status}"

    @property
    def is_successful(self):
        return self.status == "success"

