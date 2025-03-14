from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from custom_admin import custom_admin_site  # Import the custom admin site

urlpatterns = [
    path('admin/', custom_admin_site.urls),  # Use the custom admin site
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
