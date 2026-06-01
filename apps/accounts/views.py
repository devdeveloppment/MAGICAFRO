from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LoyaltyAccount


@login_required
def profile(request):
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'accounts/profile.html', {'orders': orders})


@login_required
def rewards(request):
    """Vue du programme de fidélité Magic Rewards."""
    loyalty, created = LoyaltyAccount.objects.get_or_create(user=request.user)

    # Calcul du prochain palier
    tier_thresholds = {
        'BRONZE': {'next': 'SILVER', 'points_needed': 500, 'label': 'Argent'},
        'SILVER': {'next': 'GOLD', 'points_needed': 1500, 'label': 'Or'},
        'GOLD': {'next': 'DIAMOND', 'points_needed': 5000, 'label': 'Diamant'},
        'DIAMOND': {'next': None, 'points_needed': 0, 'label': 'Maximum atteint'},
    }

    current_tier_info = tier_thresholds.get(loyalty.tier, tier_thresholds['BRONZE'])
    if current_tier_info['next']:
        progress = min(100, int((loyalty.points / current_tier_info['points_needed']) * 100))
        points_remaining = max(0, current_tier_info['points_needed'] - loyalty.points)
    else:
        progress = 100
        points_remaining = 0

    # Historique des commandes récentes
    recent_orders = request.user.orders.filter(status='DELIVERED').order_by('-created_at')[:5]

    context = {
        'loyalty': loyalty,
        'tier_info': current_tier_info,
        'progress': progress,
        'points_remaining': points_remaining,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/rewards.html', context)


def register(request):
    from .forms import CustomUserCreationForm
    from django.contrib.auth import login
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Inscription réussie ! Bienvenue sur MagicAfro.')
            return redirect('accounts:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
