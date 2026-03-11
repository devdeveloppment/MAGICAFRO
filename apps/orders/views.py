from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product
from .cart import Cart
from django.http import JsonResponse

from .forms import OrderCreateForm
from .models import OrderItem

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'cart_count': len(cart),
            'cart_total': float(cart.get_total_price())
        })
    return redirect('orders:cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('orders:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    return render(request, 'orders/cart_detail.html', {'cart': cart})

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.total = cart.get_total_price()
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    unit_price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            
            # If CinetPay, redirect to payment initiation
            if order.payment_method == 'CINETPAY':
                return redirect('payments:initiate_cinetpay', order_id=order.id)
            elif order.payment_method == 'STRIPE':
                return redirect('payments:stripe_payment', order_id=order.id)
                
            # Otherwise show success page
            return render(request, 'orders/created.html', {'order': order})
    else:
        # Pre-fill with user info if logged in
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': f"{request.user.first_name} {request.user.last_name}",
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
