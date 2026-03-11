import requests
import json
import time
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from orders.models import Order
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

def stripe_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    success_url = request.build_absolute_uri(reverse('payments:payment_done'))
    cancel_url = request.build_absolute_uri(reverse('payments:payment_cancelled'))
    
    # Create Stripe checkout session
    session_data = {
        'mode': 'payment',
        'client_reference_id': order.id,
        'success_url': success_url,
        'cancel_url': cancel_url,
        'line_items': []
    }
    
    # Add order items to line items
    for item in order.items.all():
        session_data['line_items'].append({
            'price_data': {
                'unit_amount': int(item.unit_price * 100),
                'currency': 'xof',
                'product_data': {
                    'name': item.product.name,
                },
            },
            'quantity': item.quantity,
        })
        
    session = stripe.checkout.Session.create(**session_data)
    return redirect(session.url, code=303)

def initiate_cinetpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    url = "https://api-checkout.cinetpay.com/v2/payment"
    
    transaction_id = f"{order.id}{int(time.time())}"
    
    # Orders are already in FCFA (XOF)
    amount_xof = int(order.total)
    
    data = {
        "apikey": settings.CINETPAY_API_KEY,
        "site_id": settings.CINETPAY_SITE_ID,
        "transaction_id": transaction_id,
        "amount": amount_xof,
        "currency": "XOF", 
        "description": f"Commande MagicAfro {order.id}",
        "notify_url": request.build_absolute_uri(reverse('payments:cinetpay_notify')),
        "return_url": request.build_absolute_uri(reverse('payments:payment_done')),
        "channels": "ALL",
        "metadata": "",
        "lang": "fr",
        "customer_id": str(order.id),
        "customer_name": order.full_name.split()[0] if ' ' in order.full_name else order.full_name,
        "customer_surname": order.full_name.split()[-1] if ' ' in order.full_name else "Client",
        "customer_email": order.email,
        "customer_phone_number": order.phone,
        "customer_address": order.street_address,
        "customer_city": order.city,
        "customer_country": "CI", 
        "customer_state": order.city,
        "customer_zip_code": order.postal_code,
    }
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, data=json.dumps(data), headers=headers)
        res_data = response.json()
        print(f"CinetPay Response: {res_data}")
        
        if res_data.get('code') == '201':
            payment_url = res_data.get('data', {}).get('payment_url')
            order.transaction_id = res_data.get('data', {}).get('payment_token')
            order.save()
            return redirect(payment_url)
        else:
            return render(request, 'payments/error.html', {'error': res_data.get('message'), 'order': order})
    except Exception as e:
        return render(request, 'payments/error.html', {'error': str(e), 'order': order})

@csrf_exempt
def cinetpay_notify(request):
    if request.method == 'POST':
        transaction_id = request.POST.get('cpm_trans_id')
        
        if not transaction_id:
            return HttpResponse("Invalid data", status=400)
            
        v_url = "https://api-checkout.cinetpay.com/v2/payment/check"
        v_data = {
            "apikey": settings.CINETPAY_API_KEY,
            "site_id": settings.CINETPAY_SITE_ID,
            "transaction_id": transaction_id
        }
        
        try:
            response = requests.post(v_url, json=v_data)
            res_data = response.json()
            
            if res_data.get('code') == '00':
                order_id = transaction_id.split('_')[0]
                order = Order.objects.get(id=order_id)
                order.payment_status = True
                order.status = 'PAID'
                order.save()
                return HttpResponse("OK")
        except Exception as e:
            return HttpResponse(str(e), status=500)
            
    return HttpResponse("Method not allowed", status=405)

def payment_done(request):
    return render(request, 'payments/done.html')

def payment_cancelled(request):
    return render(request, 'payments/cancelled.html')
