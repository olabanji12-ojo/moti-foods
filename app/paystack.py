from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import * 
from .forms import CustomerCreationForm

from django.http import JsonResponse
import json
from decimal import Decimal
import requests
from django.conf import settings



# Change the function name and parameter to avoid confusion
def paystack_checkout(payload):  # Rename from 'checkout' to 'paystack_checkout'
    """Initialize Paystack payment"""
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        'https://api.paystack.co/transaction/initialize',
        headers=headers, 
        data=json.dumps(payload)
    )
    response_data = response.json() 

    if response_data.get('status') == True:
        return True, response_data['data']['authorization_url']
    else:
        error_message = response_data.get('message', 'Failed to initiate payment')
        return False, error_message

def verify_payment(reference):
    """
    Verify payment with Paystack to make sure it's real
    """
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }
    
    response = requests.get(
        f'https://api.paystack.co/transaction/verify/{reference}',
        headers=headers
    )
    
    response_data = response.json()
    
    if response_data.get('status') and response_data['data']['status'] == 'success':
        return True
    return False


