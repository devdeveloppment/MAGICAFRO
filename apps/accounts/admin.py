from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Address, BeautyProfile, LoyaltyAccount


class AddressInline(admin.StackedInline):
    model = Address
    extra = 0


class BeautyProfileInline(admin.StackedInline):
    model = BeautyProfile
    extra = 0
    can_delete = False


class LoyaltyAccountInline(admin.StackedInline):
    model = LoyaltyAccount
    extra = 0
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    list_filter = ['is_staff', 'is_superuser', 'is_active']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    inlines = [AddressInline, BeautyProfileInline, LoyaltyAccountInline]


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'points', 'tier', 'total_spent', 'created_at']
    list_filter = ['tier']
    search_fields = ['user__email', 'user__first_name']
    readonly_fields = ['created_at']
