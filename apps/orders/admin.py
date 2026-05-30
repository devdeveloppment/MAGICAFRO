from django.contrib import admin
from .models import Order, OrderItem, Subscription


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'created_at']
    search_fields = ['full_name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [OrderItemInline]
    list_editable = ['status', 'payment_status']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'frequency', 'is_active', 'next_delivery_date', 'created_at']
    list_filter = ['is_active', 'frequency']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['created_at']
    list_editable = ['is_active']
