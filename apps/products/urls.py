from django.urls import path
from .views import home, product_list, product_detail

app_name = 'products'

urlpatterns = [
    path('', home, name='home'),
    path('boutique/', product_list, name='product_list'),
    path('boutique/<slug:category_slug>/', product_list, name='product_list_by_category'),
    path('produit/<slug:slug>/', product_detail, name='product_detail'),
]
