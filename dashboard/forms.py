from django import forms
from products.models import Product, Category

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}))
    additional_images = forms.FileField(widget=MultipleFileInput(attrs={'multiple': True, 'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}), required=False)

    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'price', 'old_price', 'stock', 'badge', 'is_active', 'video']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'category': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'description': forms.Textarea(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'old_price': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'badge': forms.Select(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-6 h-6 rounded border-gray-300 text-accent focus:ring-accent'}),
            'video': forms.FileInput(attrs={'class': 'w-full bg-gray-50 border border-gray-100 rounded-2xl px-6 py-4 outline-none focus:border-accent transition font-bold text-dark', 'accept': 'video/*'}),
        }
