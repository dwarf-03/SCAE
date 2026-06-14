from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # Lista de clientes
    path('', views.lista, name='lista'),

    # Crear cliente
    path('crear/', views.crear, name='crear'),

    # Detalle del cliente
    path('detalle/<int:pk>/', views.detalle, name='detalle'),

    # Editar cliente
    path('editar/<int:pk>/', views.editar, name='editar'),

    # Eliminar cliente
    path('eliminar/<int:pk>/', views.eliminar, name='eliminar'),
]