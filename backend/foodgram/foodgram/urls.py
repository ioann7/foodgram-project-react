from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

api_urls = [
    path('', include('users.urls')),
    path('', include('recipes.urls')),
]

urlpatterns = [
    path('api/', include(api_urls)),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
