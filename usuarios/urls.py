from django.urls import path
from . import views

urlpatterns = [
    # Página de login
    path('', views.login_view, name='login'),

    # Cerrar sesión
    path('logout/', views.logout_view, name='logout'),

    # Dashboard principal
    path('dashboard/', views.dashboard, name='dashboard'),
]