from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # URLs de cada módulo
    path('', include('usuarios.urls')),
    path('inventario/', include('inventario.urls')),
    path('clientes/', include('clientes.urls')),
    path('alquileres/', include('alquileres.urls')),
    path('devoluciones/', include('devoluciones.urls')),
    path('multas/', include('multas.urls')),
    path('reportes/', include('reportes.urls')),
    path('notificaciones/', include('notificaciones.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('auditoria/', include('auditoria.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)