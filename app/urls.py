from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('product_page/', views.product_page, name='product_page'),
    path('product_id/<int:id>/', views.product_id, name='product_id'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('login_page/', views.login_page, name='login_page'),
    path('register_page/', views.register_page, name='register_page'),
    path('logout_page/', views.logout_page, name='logout_page'),
    path('update_cart/', views.update_cart, name='update_cart'),
    path('create-checkout/', views.create_paystack_checkout_session, name='create-checkout'),
    path('initiate-payment/', views.initiate_payment, name='initiate-payment'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('webhook/paystack/', views.paystack_webhook, name='paystack-webhook'),
    

]

