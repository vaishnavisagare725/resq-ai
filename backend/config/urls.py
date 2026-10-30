from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path


def health(request):
    """The host uses this to check the app is alive. The website calls it to wake a sleeping server."""
    return HttpResponse('ok')


urlpatterns = [
    path('health/', health),
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('incidents.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

if settings.DEBUG:
    # on my laptop, Django serves uploaded photos. In production they live on Cloudinary.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)