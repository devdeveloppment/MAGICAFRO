from django import forms
from products.models import Product, Category

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}))

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'old_price', 'stock', 'badge', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'category': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'old_price': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'badge': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-6 h-6 rounded border-gray-300 text-accent focus:ring-accent'}),
        }
