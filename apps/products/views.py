from django.shortcuts import render, get_object_or_404, redirect
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, ProductImage, Review, ReviewMedia
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
        Product.objects.select_related('category').prefetch_related('images', 'reviews__user', 'reviews__media'),
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

@login_required
def submit_review(request, slug):
    """Soumettre un avis avec photos et gagner des points de fidélité."""
    product = get_object_or_404(Product, slug=slug, is_active=True)

    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        comment = request.POST.get('comment', '')

        # Créer l'avis
        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=int(rating),
            comment=comment,
            is_verified=product.orders_containing(request.user) if hasattr(product, 'orders_containing') else False,
        )

        # Sauvegarder les photos uploadées
        photos = request.FILES.getlist('photos')
        for photo in photos[:5]:  # Max 5 photos
            ReviewMedia.objects.create(review=review, file=photo)

        # Attribuer des points de fidélité (+25 pts par avis)
        try:
            from accounts.models import LoyaltyAccount
            loyalty, _ = LoyaltyAccount.objects.get_or_create(user=request.user)
            loyalty.points += 25
            loyalty.save()
            messages.success(request, f'Merci pour votre avis ! Vous avez gagné 25 points Magic Rewards. 🎉')
        except Exception:
            messages.success(request, 'Merci pour votre avis !')

    return redirect('products:product_detail', slug=slug)

def beauty_diagnostic(request):
    """
    Diagnostic IA: Analyze user input and return tailored recommendations.
    Saves to BeautyProfile if the user is authenticated.
    """
    if request.method == 'POST':
        hair_type = request.POST.get('hair_type')
        porosity = request.POST.get('porosity')
        concern = request.POST.get('concern')
        
        # Sauvegarde du profil si connecté
        if request.user.is_authenticated:
            from accounts.models import BeautyProfile
            profile, _ = BeautyProfile.objects.get_or_create(user=request.user)
            profile.hair_type = hair_type
            profile.hair_porosity = porosity
            profile.primary_concern = concern
            profile.save()
            
        # Moteur de recommandation basique
        recommended_products = Product.objects.filter(is_active=True)
        if concern == 'Hydratation':
            recommended_products = recommended_products.filter(Q(description__icontains='hydrat') | Q(name__icontains='hydrat'))
        elif concern == 'Pousse':
            recommended_products = recommended_products.filter(Q(description__icontains='pousse') | Q(name__icontains='pousse') | Q(description__icontains='croissance'))
        elif concern == 'Réparation':
            recommended_products = recommended_products.filter(Q(description__icontains='répar') | Q(name__icontains='répar') | Q(description__icontains='fort'))
            
        # Fallback si pas de résultat exact
        if not recommended_products.exists():
            recommended_products = Product.objects.filter(is_active=True).order_by('-rating_avg')[:4]
        else:
            recommended_products = recommended_products[:4]
            
        return render(request, 'products/diagnostic_results.html', {
            'products': recommended_products,
            'concern': concern,
            'hair_type': hair_type
        })

    return render(request, 'products/diagnostic.html')

