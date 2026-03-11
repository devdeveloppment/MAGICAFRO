from django.db import models
from django.conf import settings

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENT', 'Pourcentage (%)'),
        ('FIXED', 'Montant Fixe (CFA/EUR)'),
    ]
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

class Testimonial(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True)
    photo = models.ImageField(upload_to='testimonials/', null=True, blank=True)
    rating = models.IntegerField(default=5)
    comment = models.TextField()
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testimonial from {self.name}"
