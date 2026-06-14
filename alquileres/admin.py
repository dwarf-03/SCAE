from django.contrib import admin
from .models import Alquiler, DetalleAlquiler, Reserva

# Detalles del alquiler como tabla inline
class DetalleAlquilerInline(admin.TabularInline):
    model = DetalleAlquiler
    extra = 1
    readonly_fields = ['subtotal']

@admin.register(Alquiler)
class AlquilerAdmin(admin.ModelAdmin):
    list_display = ['numero', 'cliente', 'fecha_inicio', 'fecha_fin',
                    'estado', 'total', 'pagado', 'canal']
    list_filter = ['estado', 'pagado', 'canal']
    search_fields = ['numero', 'cliente__usuario__first_name',
                    'cliente__numero_documento']
    readonly_fields = ['numero', 'fecha_creacion', 'fecha_actualizacion']
    inlines = [DetalleAlquilerInline]

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'herramienta', 'cantidad',
                    'fecha_inicio', 'fecha_fin', 'estado']
    list_filter = ['estado']
    search_fields = ['cliente__usuario__first_name', 'herramienta__nombre']