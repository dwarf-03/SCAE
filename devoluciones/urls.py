from django.urls import path
from . import views

app_name = 'devoluciones'

urlpatterns = [
    # Lista de devoluciones
    path('', views.lista, name='lista'),

    # Recibir herramienta de un alquiler
    path('recibir/<int:pk>/', views.recibir, name='recibir'),

    # Detalle de devolución
    path('detalle/<int:pk>/', views.detalle, name='detalle'),
]