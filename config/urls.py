from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashbord/', lambda r: redirect('/dashboard/', permanent=True)),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('marketing/', include('marketing.urls', namespace='marketing')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('', include('products.urls', namespace='products')),
]

# Servir les fichiers médias et statiques (développement + Railway)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

