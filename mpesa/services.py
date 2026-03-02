import requests
import base64
import json
import logging
from datetime import datetime
from django.conf import settings
from .models import MpesaTransaction

logger = logging.getLogger(__name__)

def get_access_token():
    """Generate OAuth token from Safaricom"""
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    try:
        response = requests.get(api_url, auth=(consumer_key, consumer_secret))
        response.raise_for_status()
        token = response.json().get('access_token')
        return token
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get access token: {e}")
        return None

def initiate_stk_push(phone_number, amount, account_reference, transaction_desc, user=None, product=None, transaction_type='product_purchase'):
    """
    Initiate STK push to customer phone
    Returns: tuple (success, response_data or error_message, transaction_id)
    """
    access_token = get_access_token()
    if not access_token:
        return False, "Failed to obtain access token", None
    
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(amount),  # Ensure integer
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": account_reference[:12],  # Max 12 chars
        "TransactionDesc": transaction_desc[:13]  # Max 13 chars
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        
        # Log response
        logger.info(f"STK Push response: {result}")
        
        # Create transaction record
        transaction = MpesaTransaction.objects.create(
        user=user,
        product=product,
        seller=user if transaction_type == 'seller_verification' else None,
        transaction_type=transaction_type,
        phone_number=phone_number,
        amount=amount,
        reference=account_reference,
        description=transaction_desc,
        merchant_request_id=result.get('MerchantRequestID'),
        checkout_request_id=result.get('CheckoutRequestID'),
        response_code=result.get('ResponseCode'),
        response_description=result.get('ResponseDescription'),
        status='Pending'
    )
        
        if result.get('ResponseCode') == '0':
            return True, "STK Push sent successfully", transaction.id
        else:
            return False, result.get('ResponseDescription', 'Unknown error'), transaction.id
            
    except requests.exceptions.RequestException as e:
        logger.error(f"STK Push request failed: {e}")
        return False, str(e), None
    
    
def query_stk_status(checkout_request_id):
    """Query the status of an STK push transaction"""
    access_token = get_access_token()
    if not access_token:
        return None
    
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(
        (settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()
    ).decode()
    
    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "CheckoutRequestID": checkout_request_id
    }
    
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Query status failed: {e}")
        return None