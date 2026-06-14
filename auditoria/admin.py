from django.contrib import admin
from .models import Auditoria

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    # Auditoría es solo lectura, nadie debe modificarla
    list_display = ['usuario', 'accion', 'modulo',
                    'registro_id', 'ip_address', 'fecha_accion']
    list_filter = ['accion', 'modulo']
    search_fields = ['usuario__username', 'modulo', 'descripcion']
    readonly_fields = ['usuario', 'accion', 'modulo', 'registro_id',
                    'descripcion', 'datos_anteriores', 'datos_nuevos',
                    'ip_address', 'user_agent', 'fecha_accion']

    def has_add_permission(self, request):
        # Nadie puede crear auditorías manualmente
        return False

    def has_delete_permission(self, request, obj=None):
        # Nadie puede eliminar registros de auditoría
        return False