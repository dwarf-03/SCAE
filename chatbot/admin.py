from django.contrib import admin
from .models import SesionChat, MensajeChat, IntenciónBot, RespuestaRapida

# Mensajes del chat como tabla inline
class MensajeChatInline(admin.TabularInline):
    model = MensajeChat
    extra = 0
    # Mensajes son solo lectura para mantener historial
    readonly_fields = ['tipo', 'contenido', 'intencion',
                    'confianza', 'fecha_envio']

@admin.register(SesionChat)
class SesionChatAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'numero_whatsapp', 'canal',
                    'activa', 'fecha_inicio']
    list_filter = ['canal', 'activa']
    search_fields = ['usuario__username', 'numero_whatsapp']
    readonly_fields = ['fecha_inicio', 'fecha_actualizacion']
    inlines = [MensajeChatInline]

@admin.register(IntenciónBot)
class IntenciónBotAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion', 'activo', 'fecha_creacion']
    list_filter = ['activo']
    search_fields = ['nombre', 'palabras_clave']

@admin.register(RespuestaRapida)
class RespuestaRapidaAdmin(admin.ModelAdmin):
    list_display = ['intencion', 'texto', 'valor', 'orden']
    list_filter = ['intencion']