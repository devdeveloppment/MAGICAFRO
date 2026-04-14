from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from orders.models import Order
from products.models import Product, Category
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .forms import ProductForm

def debug_images(request):
    """Page de diagnostic pour vérifier le stockage des images."""
    from products.models import ProductImage
    from django.conf import settings
    
    images = ProductImage.objects.all().order_by('-id')[:10]
    data = {
        'DEFAULT_FILE_STORAGE': settings.DEFAULT_FILE_STORAGE,
        'CLOUDINARY_CLOUD_NAME': settings.CLOUDINARY_STORAGE.get('CLOUD_NAME', 'NON DEFINI'),
        'images': [
            {
                'id': img.id,
                'product': img.product.name,
                'image_name': str(img.image),
                'image_url': img.image.url if img.image else 'AUCUNE IMAGE',
                'is_feature': img.is_feature,
            }
            for img in images
        ]
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
    # Stats
    total_sales = Order.objects.filter(payment_status=True).aggregate(Sum('total'))['total__sum'] or 0
    orders_count = Order.objects.count()
    pending_orders = Order.objects.filter(status='PENDING').count()
    products_count = Product.objects.count()
    
    # Recent orders
    recent_orders = Order.objects.all().order_by('-created_at')[:10]
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock__lte=5).order_by('stock')[:5]
    
    # Sales Data for Chart (last 7 days)
    today = timezone.now().date()
    days = []
    sales_data = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        days.append(day.strftime('%d %b'))
        day_sales = Order.objects.filter(
            created_at__date=day, 
            payment_status=True
        ).aggregate(Sum('total'))['total__sum'] or 0
        sales_data.append(float(day_sales))

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
    orders = Order.objects.all().order_by('-created_at')
    
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
def product_list(request):
    products = Product.objects.all().order_by('-created_at')
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
            image = form.cleaned_data.get('image')
            if image:
                from products.models import ProductImage
                ProductImage.objects.create(product=product, image=image, is_feature=True)
            return redirect('dashboard:product_list')
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
            image = form.cleaned_data.get('image')
            if image:
                from products.models import ProductImage
                # Delete old images if replaced, or just add a new one as feature
                product.images.all().delete()
                ProductImage.objects.create(product=product, image=image, is_feature=True)
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
