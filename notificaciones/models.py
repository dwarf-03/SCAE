from django.db import models
from usuarios.models import Usuario
from clientes.models import Cliente

class PlantillaNotificacion(models.Model):
    TIPO_CHOICES = [
        ('recordatorio_3dias', 'Recordatorio 3 Días'),
        ('recordatorio_1dia', 'Recordatorio 1 Día'),
        ('vencimiento', 'Vencimiento'),
        ('multa', 'Multa Generada'),
        ('confirmacion', 'Confirmación Alquiler'),
        ('devolucion', 'Confirmación Devolución'),
    ]

    CANAL_CHOICES = [
        ('email', 'Correo Electrónico'),
        ('whatsapp', 'WhatsApp'),
        ('ambos', 'Ambos'),
    ]

    # Tipo de notificación que representa esta plantilla
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES, unique=True)

    # Asunto del correo electrónico
    asunto = models.CharField(max_length=200)

    # Cuerpo del mensaje con variables dinámicas
    mensaje = models.TextField(help_text='Variables: {nombre}, {numero_alquiler}, {fecha_fin}, {dias_restantes}, {monto}')

    # Canal por donde se enviará la notificación
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='ambos')

    # Indica si esta plantilla está activa
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Plantilla de Notificación'
        verbose_name_plural = 'Plantillas de Notificaciones'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.canal}'


class Notificacion(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('fallida', 'Fallida'),
        ('leida', 'Leída'),
    ]

    CANAL_CHOICES = [
        ('email', 'Correo Electrónico'),
        ('whatsapp', 'WhatsApp'),
    ]

    # Cliente destinatario de la notificación
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE,
                                related_name='notificaciones')

    # Plantilla utilizada para esta notificación
    plantilla = models.ForeignKey(PlantillaNotificacion, on_delete=models.SET_NULL,
                                  null=True, related_name='notificaciones')

    # Canal por donde se envió la notificación
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)

    # Asunto del mensaje enviado
    asunto = models.CharField(max_length=200)

    # Contenido final del mensaje enviado
    mensaje = models.TextField()

    # Estado actual del envío
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Número de intentos de envío realizados
    intentos = models.PositiveIntegerField(default=0)

    # Mensaje de error si falló el envío
    error = models.TextField(blank=True, null=True)

    # Fecha en que se envió exitosamente
    fecha_envio = models.DateTimeField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.cliente} - {self.canal} - {self.estado}'

    def marcar_enviada(self):
        # Marca la notificación como enviada exitosamente
        from django.utils import timezone
        self.estado = 'enviada'
        self.fecha_envio = timezone.now()
        self.save()

    def marcar_fallida(self, error):
        # Registra el error y marca la notificación como fallida
        self.estado = 'fallida'
        self.error = error
        self.intentos += 1
        self.save()


class ConfiguracionWhatsApp(models.Model):
    # Token de acceso de la API de WhatsApp Business
    token = models.CharField(max_length=500)

    # ID del número de teléfono de WhatsApp Business
    phone_number_id = models.CharField(max_length=100)

    # Token de verificación del webhook
    webhook_verify_token = models.CharField(max_length=200)

    # Indica si la integración está activa
    activo = models.BooleanField(default=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración WhatsApp'
        verbose_name_plural = 'Configuraciones WhatsApp'

    def __str__(self):
        return f'WhatsApp Config - {self.phone_number_id}'