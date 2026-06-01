from django.urls import path, include
from .views import profile, rewards, register

app_name = 'accounts'

urlpatterns = [
    path('profile/', profile, name='profile'),
    path('rewards/', rewards, name='rewards'),
    path('register/', register, name='register'),
    path('', include('django.contrib.auth.urls')),
]
