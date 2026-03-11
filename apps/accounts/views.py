from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'accounts/profile.html', {'orders': orders})
