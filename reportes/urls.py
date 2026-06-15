from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    # Vista principal
    path('', views.lista, name='lista'),

    # Vistas con filtros
    path('inventario/', views.reporte_inventario, name='inventario'),
    path('alquileres/', views.reporte_alquileres, name='alquileres'),
    path('multas/', views.reporte_multas, name='multas'),

    # Descargas PDF con filtros
    path('inventario/pdf/', views.reporte_inventario_pdf, name='inventario_pdf'),
    path('alquileres/pdf/', views.reporte_alquileres_pdf, name='alquileres_pdf'),
    path('multas/pdf/', views.reporte_multas_pdf, name='multas_pdf'),

    # Descargas Excel con filtros
    path('inventario/excel/', views.reporte_inventario_excel, name='inventario_excel'),
    path('alquileres/excel/', views.reporte_alquileres_excel, name='alquileres_excel'),
    path('multas/excel/', views.reporte_multas_excel, name='multas_excel'),
]