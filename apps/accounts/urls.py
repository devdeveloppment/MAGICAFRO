from django.urls import path, include
from .views import profile, rewards

app_name = 'accounts'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('rewards/', rewards, name='rewards'),
    path('', include('django.contrib.auth.urls')),
]
