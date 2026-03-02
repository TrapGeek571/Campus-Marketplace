import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from .models import MpesaTransaction
from django.contrib import messages
from django.urls import reverse
from marketplace.models import Product
from .services import initiate_stk_push

logger = logging.getLogger(__name__)

@login_required
def initiate_payment(request, product_id):
    """Handle payment initiation from product page"""
    if request.method != 'POST':
        return redirect('marketplace:product_detail', product_id=product_id)
    
    product = get_object_or_404(Product, id=product_id, is_sold=False)
    phone_number = request.POST.get('phone_number', '').strip()
    
    # Basic validation
    if not phone_number:
        messages.error(request, 'Phone number is required.')
        return redirect('marketplace:product_detail', product_id=product_id)
    
    # Format phone number to 254XXXXXXXXX
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('7'):
        phone_number = '254' + phone_number
    
    amount = product.price
    account_reference = f"PROD{product.id}"
    transaction_desc = f"Payment for {product.title}"
    
    success, message, transaction_id = initiate_stk_push(
        phone_number=phone_number,
        amount=amount,
        account_reference=account_reference,
        transaction_desc=transaction_desc,
        user=request.user,
        product=product
    )
    
    if success:
        messages.success(request, 'STK Push sent! Please check your phone and enter PIN.')
        return redirect('marketplace:payment_status', transaction_id=transaction_id)
    else:
        messages.error(request, f'Payment initiation failed: {message}')
        return redirect('marketplace:product_detail', product_id=product_id)

@csrf_exempt
def mpesa_callback(request):
    """
    Callback URL for Mpesa API to send payment confirmation.
    Safaricom will POST JSON data to this endpoint.
    """
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"Mpesa Callback Received: {callback_data}")
            
            # Extract relevant info
            stk_callback = callback_data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            # Find transaction by checkout_request_id
            try:
                transaction = MpesaTransaction.objects.get(checkout_request_id=checkout_request_id)
                transaction.callback_metadata = callback_data
                
                if result_code == 0:
                    # Success: extract payment details
                    callback_metadata = stk_callback.get('CallbackMetadata', {})
                    items = callback_metadata.get('Item', [])
                    # You can extract amount, receipt, etc.
                    for item in items:
                        if item.get('Name') == 'Amount':
                            transaction.amount = item.get('Value')
                        elif item.get('Name') == 'MpesaReceiptNumber':
                            transaction.reference = item.get('Value')  # Overwrite with receipt
                        elif item.get('Name') == 'PhoneNumber':
                            transaction.phone_number = item.get('Value')
                    
                    transaction.status = 'Completed'
                    
                    if transaction.transaction_type == 'seller_verification':
                        # Activate seller profile
                        seller_profile = transaction.user.seller_profile
                        seller_profile.activate_verified(duration_days=30)  # 30 days
                        messages.success(transaction.user, 'Congratulations! You are now a verified seller.')
                    elif transaction.transaction_type == 'product_purchase' and transaction.product:
                        transaction.product.is_sold = True
                        transaction.product.save()
                        
                    # If transaction is linked to a product, mark it as sold
                    if transaction.product:
                        transaction.product.is_sold = True
                        transaction.product.save()
                        
                else:
                    transaction.status = 'Failed'
                    transaction.response_description = result_desc
                
                transaction.save()
                logger.info(f"Transaction {transaction.id} updated to {transaction.status}")
                
            except MpesaTransaction.DoesNotExist:
                logger.error(f"No transaction found for CheckoutRequestID: {checkout_request_id}")
            
            # Always respond with success to Safaricom
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
            
        except Exception as e:
            logger.exception("Error processing callback")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Internal error"})
    
    return HttpResponse("OK")

def payment_status(request, transaction_id):
    """Show payment status page"""
    transaction = get_object_or_404(MpesaTransaction, id=transaction_id)
    # Optionally query status from Daraja
    return render(request, 'mpesa/payment_status.html', {'transaction': transaction})

@login_required
def become_verified(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number', '').strip()
        if not phone_number:
            messages.error(request, 'Phone number is required.')
            return redirect('mpesa:become_verified')
        
        # Format phone
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]
        elif phone_number.startswith('7'):
            phone_number = '254' + phone_number
        
        amount = 150
        account_reference = f"VERIFY{request.user.id}"
        transaction_desc = "Seller verification fee"
        
        success, message, transaction_id = initiate_stk_push(
            phone_number=phone_number,
            amount=amount,
            account_reference=account_reference,
            transaction_desc=transaction_desc,
            user=request.user,
            transaction_type='seller_verification'  # We need to pass this to services
        )
        
        if success:
            messages.success(request, 'STK Push sent! Please check your phone and enter PIN.')
            return redirect('mpesa:verification_status', transaction_id=transaction_id)
        else:
            messages.error(request, f'Payment initiation failed: {message}')
            return redirect('mpesa:become_verified')
    
    return render(request, 'mpesa/become_verified.html')
