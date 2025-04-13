from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from customer.health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('customer.urls')),
    path('health/', health_check, name='health_check'),
]

# Always serve static files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
