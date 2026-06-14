from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    # Lista de herramientas
    path('', views.lista, name='lista'),

    # Crear herramienta
    path('crear/', views.crear, name='crear'),

    # Editar herramienta
    path('editar/<int:pk>/', views.editar, name='editar'),

    # Detalle de herramienta
    path('detalle/<int:pk>/', views.detalle, name='detalle'),

    # Eliminar herramienta
    path('eliminar/<int:pk>/', views.eliminar, name='eliminar'),

    # Gestión de categorías
    path('categorias/', views.categorias, name='categorias'),
]