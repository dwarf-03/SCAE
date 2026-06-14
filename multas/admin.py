from django.contrib import admin
from .models import ConfiguracionMulta, Multa, PagoMulta

# Pagos de multa como tabla inline
class PagoMultaInline(admin.TabularInline):
    model = PagoMulta
    extra = 1

@admin.register(ConfiguracionMulta)
class ConfiguracionMultaAdmin(admin.ModelAdmin):
    # Solo permite editar, no crear múltiples configuraciones
    list_display = ['valor_por_dia', 'porcentaje_adicional',
                    'dias_gracia', 'activo', 'fecha_actualizacion']

@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    list_display = ['alquiler', 'cliente', 'dias_retraso',
                    'monto_total', 'estado', 'fecha_creacion']
    list_filter = ['estado']
    search_fields = ['alquiler__numero', 'cliente__usuario__first_name']
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [PagoMultaInline]

@admin.register(PagoMulta)
class PagoMultaAdmin(admin.ModelAdmin):
    list_display = ['multa', 'monto', 'metodo_pago',
                    'referencia', 'fecha_pago']
    list_filter = ['metodo_pago']