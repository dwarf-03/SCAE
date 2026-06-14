from django.urls import path
from . import views

app_name = 'multas'

urlpatterns = [
    # Lista de multas
    path('', views.lista, name='lista'),

    # Detalle de multa
    path('detalle/<int:pk>/', views.detalle, name='detalle'),

    # Pagar multa
    path('pagar/<int:pk>/', views.pagar, name='pagar'),

    # Condonar multa
    path('condonar/<int:pk>/', views.condonar, name='condonar'),

    # Configuración de multas
    path('configuracion/', views.configuracion, name='configuracion'),
]