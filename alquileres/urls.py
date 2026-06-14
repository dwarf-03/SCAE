from django.urls import path
from . import views

app_name = 'alquileres'

urlpatterns = [
    # Lista de alquileres
    path('', views.lista, name='lista'),

    # Crear alquiler
    path('crear/', views.crear, name='crear'),

    # Detalle del alquiler
    path('detalle/<int:pk>/', views.detalle, name='detalle'),

    # Cancelar alquiler
    path('cancelar/<int:pk>/', views.cancelar, name='cancelar'),
]