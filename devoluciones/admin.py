from django.contrib import admin
from .models import Devolucion, DetalleDevolucion

# Detalles de devolución como tabla inline
class DetalleDevolucionInline(admin.TabularInline):
    model = DetalleDevolucion
    extra = 1
    readonly_fields = ['costo_dano']

@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ['alquiler', 'recibido_por', 'fecha_devolucion',
                    'estado', 'tiene_multa', 'fue_a_tiempo']
    list_filter = ['estado', 'tiene_multa']
    search_fields = ['alquiler__numero', 'alquiler__cliente__usuario__first_name']
    readonly_fields = ['fecha_creacion']
    inlines = [DetalleDevolucionInline]

@admin.register(DetalleDevolucion)
class DetalleDevolucionAdmin(admin.ModelAdmin):
    list_display = ['devolucion', 'detalle_alquiler',
                    'cantidad_devuelta', 'condicion', 'costo_dano']
    list_filter = ['condicion']