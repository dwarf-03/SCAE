from django.contrib import admin
from .models import Categoria, Herramienta

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'fecha_creacion']
    search_fields = ['nombre']

@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'categoria', 'precio_diario', 
                    'cantidad_disponible', 'cantidad_alquilada', 'estado']
    list_filter = ['estado', 'categoria', 'activo']
    search_fields = ['codigo', 'nombre']
    readonly_fields = ['codigo_qr', 'fecha_creacion', 'fecha_actualizacion']