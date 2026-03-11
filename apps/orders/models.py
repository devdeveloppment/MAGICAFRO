from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'En attente'),
        ('PAID', 'Payée'),
        ('PROCESSING', 'En préparation'),
        ('SHIPPED', 'Expédiée'),
        ('DELIVERED', 'Livrée'),
        ('CANCELLED', 'Annulée'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('CINETPAY', 'CinetPay (Mobile Money)'),
        ('STRIPE', 'Carte Bancaire (Stripe)'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=150, default='')
    email = models.EmailField(default='')
    phone = models.CharField(max_length=20, default='')
    street_address = models.CharField(max_length=250, default='')
    postal_code = models.CharField(max_length=20, default='')
    city = models.CharField(max_length=100, default='')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='CINETPAY')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.email or (self.user.email if self.user else 'Inconnu')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else 'Produit supprimé'}"
    
    @property
    def total_price(self):
        return self.quantity * self.unit_price
