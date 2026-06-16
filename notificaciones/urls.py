from django.urls import path
from . import views

app_name = 'notificaciones'

urlpatterns = [
    # Vista web
    path('', views.lista, name='lista'),

    # Plantillas
    path('api/plantillas/', views.PlantillaListView.as_view(), name='api-plantillas'),
    path('api/plantillas/<int:pk>/', views.PlantillaDetailView.as_view(), name='api-plantilla-detail'),

    # Notificaciones
    path('api/historial/', views.NotificacionListView.as_view(), name='api-historial'),
    path('api/enviar/', views.enviar_notificacion_manual, name='api-enviar'),
]