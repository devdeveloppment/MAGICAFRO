from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order
from products.models import Product, Category, ProductImage
from django.db.models import Sum, Count, Prefetch, Q
from django.utils import timezone
from datetime import timedelta
from .forms import ProductForm

def debug_images(request):
    """Page de diagnostic pour vérifier le stockage des images."""
    from products.models import ProductImage
    from django.conf import settings

    storages = settings.STORAGES
    default_backend = storages.get('default', {}).get('BACKEND', 'NON DEFINI')
    cloud_name = settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'NON DEFINI')

    images = ProductImage.objects.all().order_by('-id')[:10]
    imgs_data = []
    for img in images:
        try:
            url = img.image.url if img.image else 'AUCUNE IMAGE'
        except Exception as e:
            url = f'ERREUR: {e}'
        imgs_data.append({
            'id': img.id,
            'product': img.product.name,
            'image_name': str(img.image),
            'image_url': url,
            'is_feature': img.is_feature,
        })

    data = {
        'DEFAULT_STORAGE_BACKEND': default_backend,
        'CLOUDINARY_CLOUD_NAME': cloud_name,
        'images': imgs_data,
    }
    return JsonResponse(data, json_dumps_params={'ensure_ascii': False, 'indent': 2})

def dashboard_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('dashboard:home')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('dashboard:home')
        else:
            messages.error(request, "E-mail ou mot de passe incorrect, ou accès refusé.")
            
    return render(request, 'dashboard/login.html')

def dashboard_logout(request):
    logout(request)
    return redirect('dashboard:login')

@login_required(login_url='dashboard:login')
def dashboard_home(request):
    # Stats optimization - aggregate multiple metrics in one query
    stats = Order.objects.aggregate(
        total_sales=Sum('total', filter=Q(payment_status=True)),
        orders_count=Count('id'),
        pending_orders=Count('id', filter=Q(status='PENDING'))
    )
    total_sales = stats['total_sales'] or 0
    orders_count = stats['orders_count']
    pending_orders = stats['pending_orders']
    products_count = Product.objects.count()
    
    # Recent orders - select_related/prefetch_related not needed if we only show basic info, 
    # but good practice if the template accesses items or user
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=5).select_related('category').order_by('stock')[:5]
    
    # Sales Data for Chart (last 7 days) - Single Query Optimization
    from django.db.models.functions import TruncDate
    today = timezone.now().date()
    start_date = today - timedelta(days=6)
    
    # Efficiently group sales by date
    sales_by_day = Order.objects.filter(
        created_at__date__gte=start_date,
        payment_status=True
    ).annotate(date=TruncDate('created_at')) \
     .values('date') \
     .annotate(day_total=Sum('total')) \
     .order_by('date')
    
    sales_dict = {item['date']: float(item['day_total']) for item in sales_by_day}
    
    days = []
    sales_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days.append(day.strftime('%d %b'))
        sales_data.append(sales_dict.get(day, 0.0))

    context = {
        'total_sales': total_sales,
        'orders_count': orders_count,
        'pending_orders': pending_orders,
        'products_count': products_count,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'days': days,
        'sales_data': sales_data,
        'segment': 'dashboard'
    }
    return render(request, 'dashboard/index.html', context)

@login_required(login_url='dashboard:login')
def order_list(request):
    status_filter = request.GET.get('status')
    orders = Order.objects.select_related('user').prefetch_related('items__product').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    context = {
        'orders': orders,
        'segment': 'orders',
        'current_status': status_filter,
        'count_all': Order.objects.count(),
        'count_pending': Order.objects.filter(status='PENDING').count(),
        'count_paid': Order.objects.filter(status='PAID').count(),
        'count_shipped': Order.objects.filter(status='SHIPPED').count(),
    }
    return render(request, 'dashboard/orders.html', context)

@login_required(login_url='dashboard:login')
def order_detail(request, pk):
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('items__product__images'),
        pk=pk
    )
    context = {
        'order': order,
        'segment': 'orders',
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'dashboard/order_detail.html', context)

@login_required(login_url='dashboard:login')
def order_update_status(request, pk):
    if request.method == 'POST':
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save(update_fields=['status', 'updated_at'])
            messages.success(request, f"Statut de la commande #{order.id} mis à jour : {order.get_status_display()}")
        else:
            messages.error(request, "Statut invalide.")
    return redirect('dashboard:order_detail', pk=pk)


@login_required(login_url='dashboard:login')
def product_list(request):
    # Optimize with select_related
    products = Product.objects.all().select_related('category').order_by('-created_at')
    context = {
        'products': products,
        'segment': 'products'
    }
    return render(request, 'dashboard/products.html', context)

@login_required(login_url='dashboard:login')
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            image = request.FILES.get('image')  # Lire directement depuis request.FILES
            if image:
                from products.models import ProductImage
                try:
                    pi = ProductImage(product=product, is_feature=True)
                    pi.image.save(image.name, image, save=True)
                    print(f"[OK] Image sauvegardée: {pi.image.url}")
                except Exception as e:
                    print(f"[ERREUR] Impossible de sauvegarder l'image: {e}")
                    messages.warning(request, f"Produit créé mais l'image n'a pas pu être sauvegardée: {e}")
            return redirect('dashboard:product_list')
        else:
            print(f"[FORM ERRORS] {form.errors}")
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Ajouter un Produit',
        'segment': 'products'
    }
    return render(request, 'dashboard/product_form.html', context)

@login_required(login_url='dashboard:login')
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            image = request.FILES.get('image')  # Lire directement depuis request.FILES
            if image:
                from products.models import ProductImage
                # Supprimer les anciennes images et créer une nouvelle
                product.images.all().delete()
                try:
                    pi = ProductImage(product=product, is_feature=True)
                    pi.image.save(image.name, image, save=True)
                    print(f"[OK] Image modifiée sauvegardée: {pi.image.url}")
                except Exception as e:
                    print(f"[ERREUR] Impossible de sauvegarder l'image: {e}")
                    messages.warning(request, f"Produit modifié mais l'image n'a pas pu être sauvegardée: {e}")
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': f'Modifier {product.name}',
        'product': product,
        'segment': 'products'
    }
    return render(request, 'dashboard/product_form.html', context)

@login_required(login_url='dashboard:login')
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('dashboard:product_list')
    return render(request, 'dashboard/product_confirm_delete.html', {'product': product})

@login_required(login_url='dashboard:login')
def customer_list(request):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # Customers who made at least one order OR are registered
    customers = User.objects.annotate(order_count=Count('orders')).order_by('-order_count')
    context = {
        'customers': customers,
        'segment': 'customers'
    }
    return render(request, 'dashboard/customers.html', context)

@login_required(login_url='dashboard:login')
def promotion_list(request):
    context = {
        'segment': 'promotions'
    }
    return render(request, 'dashboard/promotions.html', context)

@login_required(login_url='dashboard:login')
def report_list(request):
    context = {
        'segment': 'reports'
    }
    return render(request, 'dashboard/reports.html', context)
