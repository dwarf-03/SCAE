from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Lista de clientes (admin/empleado)
    path('', views.lista, name='lista'),
    path('crear/', views.crear, name='crear'),
    path('detalle/<int:pk>/', views.detalle, name='detalle'),
    path('editar/<int:pk>/', views.editar, name='editar'),
    path('eliminar/<int:pk>/', views.eliminar, name='eliminar'),

    # Panel del cliente
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('mis-alquileres/', views.mis_alquileres, name='mis_alquileres'),
    path('mis-alquileres/<int:pk>/', views.mi_alquiler_detalle, name='mi_alquiler_detalle'),
    path('mis-multas/', views.mis_multas, name='mis_multas'),
    path('mis-devoluciones/', views.mis_devoluciones, name='mis_devoluciones'),
    path('solicitar-alquiler/', views.solicitar_alquiler, name='solicitar_alquiler'),
    path('editar-perfil/', views.editar_perfil, name='editar_perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]