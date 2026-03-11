from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('cinetpay/initiate/<int:order_id>/', views.initiate_cinetpay_payment, name='initiate_cinetpay'),
    path('stripe/initiate/<int:order_id>/', views.stripe_payment, name='stripe_payment'),
    path('cinetpay/notify/', views.cinetpay_notify, name='cinetpay_notify'),
    path('done/', views.payment_done, name='payment_done'),
    path('cancelled/', views.payment_cancelled, name='payment_cancelled'),
]
