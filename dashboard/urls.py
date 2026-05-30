from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
    path('', views.dashboard_home, name='home'),
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('orders/<int:pk>/update-status/', views.order_update_status, name='order_update_status'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_create, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('customers/', views.customer_list, name='customer_list'),
    path('promotions/', views.promotion_list, name='promotion_list'),
    path('reports/', views.report_list, name='report_list'),
    path('debug-images/', views.debug_images, name='debug_images'),
]
