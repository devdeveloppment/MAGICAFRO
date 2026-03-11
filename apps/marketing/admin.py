from django.contrib import admin
from .models import Newsletter, PromoCode, Testimonial

@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    search_fields = ['email']

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'valid_to', 'is_active']
    list_filter = ['discount_type', 'is_active']
    search_fields = ['code']

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'rating', 'is_visible']
    list_filter = ['rating', 'is_visible']
