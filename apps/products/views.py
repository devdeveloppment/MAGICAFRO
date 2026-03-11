from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from marketing.models import Testimonial

def home(request):
    categories = Category.objects.filter(parent=None).order_by('order')[:6]
    best_sellers = Product.objects.filter(badge='BEST', is_active=True).order_by('-created_at')[:4]
    testimonials = Testimonial.objects.filter(is_visible=True)[:3]
    
    context = {
        'categories': categories,
        'best': best_sellers,
        'products': Product.objects.filter(is_active=True).order_by('-created_at')[:4],
        'testimonials': testimonials,
    }
    return render(request, 'index.html', context)

def product_list(request, category_slug=None):
    from django.core.paginator import Paginator
    from django.db.models import Q
    category = None
    categories = Category.objects.filter(parent=None)
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    paginator = Paginator(products, 12) # 12 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        'category': category,
        'categories': categories,
        'products': page_obj,
    }
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related': related_products,
    }
    return render(request, 'products/product_detail.html', context)
