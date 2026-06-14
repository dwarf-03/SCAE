from django.contrib import admin
from .models import PlantillaNotificacion, Notificacion, ConfiguracionWhatsApp

@admin.register(PlantillaNotificacion)
class PlantillaNotificacionAdmin(admin.ModelAdmin):
    list_display = ['tipo', 'asunto', 'canal', 'activo']
    list_filter = ['canal', 'activo']
    search_fields = ['tipo', 'asunto']

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ['cliente', 'canal', 'asunto',
                    'estado', 'intentos', 'fecha_envio']
    list_filter = ['canal', 'estado']
    search_fields = ['cliente__usuario__first_name', 'asunto']
    # Notificaciones son solo lectura para mantener integridad
    readonly_fields = ['fecha_creacion', 'fecha_envio']

@admin.register(ConfiguracionWhatsApp)
class ConfiguracionWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['phone_number_id', 'activo', 'fecha_actualizacion']
    # Token es sensible, se oculta en la lista
    readonly_fields = ['fecha_actualizacion']