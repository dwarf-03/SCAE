from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    # Vista principal del chatbot
    path('', views.index, name='index'),

    # Endpoint para enviar mensajes
    path('enviar/', views.enviar_mensaje, name='enviar_mensaje'),

    # Limpiar historial del chat
    path('limpiar/', views.limpiar_chat, name='limpiar_chat'),
]