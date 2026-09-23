from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/v1/', SpectacularAPIView.as_view(), name='schema-v1'),
    path('api/docs/v1/', SpectacularSwaggerView.as_view(url_name='schema-v1'), name='swagger-v1'),
    path('api/v1/auth/', include('apps.users.urls'))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)