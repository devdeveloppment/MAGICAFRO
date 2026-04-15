from django.shortcuts import render, get_object_or_404
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from .models import Category, Product, ProductImage
from marketing.models import Testimonial

def home(request):
    # Cache la page d'accueil 5 minutes pour éviter des requêtes répétées
    cached = cache.get('home_context')
    if not cached:
        categories = Category.objects.filter(parent=None).order_by('order').prefetch_related('products')[:6]
        products = (
            Product.objects
            .filter(is_active=True)
            .select_related('category')
            .prefetch_related(
                Prefetch('images', queryset=ProductImage.objects.filter(is_feature=True), to_attr='feature_images')
            )
            .order_by('-created_at')[:8]
        )
        testimonials = Testimonial.objects.filter(is_visible=True)[:3]
        cached = {
            'categories': list(categories),
            'products': list(products),
            'testimonials': list(testimonials),
        }
        cache.set('home_context', cached, 60 * 5)  # Cache 5 min

    return render(request, 'index.html', cached)

def product_list(request, category_slug=None):
    category = None
    categories = cache.get_or_set(
        'all_categories',
        lambda: list(Category.objects.filter(parent=None).order_by('order')),
        60 * 10  # Cache 10 min
    )

    products = (
        Product.objects
        .filter(is_active=True)
        .select_related('category')
        .prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(is_feature=True), to_attr='feature_images')
        )
        .order_by('-created_at')
    )

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

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'products/product_list.html', {
        'category': category,
        'categories': categories,
        'products': page_obj,
    })

def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images', 'reviews__user'),
        slug=slug, is_active=True
    )
    related_products = (
        Product.objects
        .filter(category=product.category, is_active=True)
        .exclude(id=product.id)
        .select_related('category')
        .prefetch_related(Prefetch('images', queryset=ProductImage.objects.filter(is_feature=True), to_attr='feature_images'))
        [:4]
    )
    return render(request, 'products/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })

    
    context = {
        'product': product,
        'related': related_products,
    }
    return render(request, 'products/product_detail.html', context)
