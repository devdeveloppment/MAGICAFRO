from django.urls import path
from .views import about, contact

app_name = 'marketing'

urlpatterns = [
    path('notre-histoire/', about, name='about'),
    path('contact/', contact, name='contact'),
]
