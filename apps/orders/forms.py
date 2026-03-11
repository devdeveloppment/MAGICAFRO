from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'street_address', 'postal_code', 'city', 'payment_method']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Nom complet'}),
            'email': forms.EmailInput(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Téléphone'}),
            'street_address': forms.Textarea(attrs={'class': 'w-full h-32 bg-gray-50 border-none rounded-2xl px-6 py-4 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Adresse de livraison', 'rows': 3}),
            'postal_code': forms.TextInput(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Code postal'}),
            'city': forms.TextInput(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition', 'placeholder': 'Ville'}),
            'payment_method': forms.Select(attrs={'class': 'w-full h-14 bg-gray-50 border-none rounded-2xl px-6 focus:ring-2 focus:ring-accent/20 transition'}),
        }
