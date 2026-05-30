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
        ('WHATSAPP', 'Commander via WhatsApp'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    full_name = models.CharField(max_length=150, default='')
    email = models.EmailField(default='', blank=True)
    phone = models.CharField(max_length=20, default='')
    street_address = models.CharField(max_length=250, default='')
    postal_code = models.CharField(max_length=20, default='', blank=True)
    city = models.CharField(max_length=100, default='Lomé')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='WHATSAPP')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    payment_status = models.BooleanField(default=False, db_index=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commande #{self.id} - {self.email or 'Invite'}"

    def get_whatsapp_url(self):
        owner_phone = "22891025232"
        message = f"🌟 *Nouvelle Commande MagicAfro #{self.id}*\n\n"
        message += f"👤 *Client:* {self.full_name}\n"
        message += f"📞 *Tel:* {self.phone}\n"
        message += f"📍 *Adresse:* {self.street_address}, {self.city}\n\n"
        message += "🛒 *Produits:*\n"
        
        for item in self.items.all():
            message += f"- {item.product.name} (x{item.quantity}) : {int(item.total_price)} FCFA\n"
            
        message += f"\n💰 *TOTAL:* {int(self.total)} FCFA\n\n"
        message += "Merci de confirmer ma commande ! ✨"
        
        import urllib.parse
        encoded_message = urllib.parse.quote(message)
        return f"https://wa.me/{owner_phone}?text={encoded_message}"

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

class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ('1_MONTH', 'Chaque mois'),
        ('2_MONTHS', 'Tous les 2 mois'),
        ('3_MONTHS', 'Tous les 3 mois'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produit abonné")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='1_MONTH', verbose_name="Fréquence de livraison")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    next_delivery_date = models.DateField(verbose_name="Prochaine livraison")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Abonnement"
        verbose_name_plural = "Abonnements"

    def __str__(self):
        return f"Abonnement {self.user.email} - {self.product.name} ({self.get_frequency_display()})"
