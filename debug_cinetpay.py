import os
import django
import requests
import json
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from orders.models import Order
from django.urls import reverse

order = Order.objects.first()
if not order:
    print("No order found")
    exit()

transaction_id = f"{order.id}{int(time.time())}"
data = {
    "apikey": settings.CINETPAY_API_KEY,
    "site_id": settings.CINETPAY_SITE_ID,
    "transaction_id": transaction_id,
    "amount": int(29 * 656), # Fixed amount for testing
    "currency": "XOF", # Fixed currency for testing
    "description": f"Test MagicAfro {order.id}",
    "notify_url": "https://example.com/notify",
    "return_url": "https://example.com/done",
    "channels": "ALL",
    "metadata": "",
    "lang": "fr",
    "customer_id": str(order.id),
    "customer_name": "Jean",
    "customer_surname": "Dupont",
    "customer_email": "jean@example.com",
    "customer_phone_number": "0123456789",
    "customer_address": "123 Rue de la Paix",
    "customer_city": "Paris",
    "customer_country": "CI",
    "customer_state": "IdF",
    "customer_zip_code": "75001",
}

url = "https://api-checkout.cinetpay.com/v2/payment"
headers = {'Content-Type': 'application/json'}

response = requests.post(url, data=json.dumps(data), headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")
