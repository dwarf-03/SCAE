from django.db import models
from usuarios.models import Usuario

class SesionChat(models.Model):
    CANAL_CHOICES = [
        ('web', 'Web'),
        ('whatsapp', 'WhatsApp'),
    ]

    # Usuario autenticado que inició el chat (puede ser anónimo)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                null=True, blank=True, related_name='sesiones_chat')

    # Número de WhatsApp si el canal es WhatsApp
    numero_whatsapp = models.CharField(max_length=20, blank=True, null=True)

    # Canal desde donde se inició la sesión
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='web')

    # Estado actual del proceso de conversación
    contexto = models.JSONField(default=dict, blank=True)

    # Indica si la sesión está activa
    activa = models.BooleanField(default=True)

    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sesión de Chat'
        verbose_name_plural = 'Sesiones de Chat'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'Sesión {self.canal} - {self.usuario or self.numero_whatsapp}'

    def actualizar_contexto(self, key, value):
        # Actualiza una clave específica del contexto de la conversación
        self.contexto[key] = value
        self.save()

    def limpiar_contexto(self):
        # Limpia el contexto al finalizar un flujo de conversación
        self.contexto = {}
        self.save()


class MensajeChat(models.Model):
    TIPO_CHOICES = [
        ('usuario', 'Usuario'),
        ('bot', 'Bot'),
    ]

    # Sesión a la que pertenece este mensaje
    sesion = models.ForeignKey(SesionChat, on_delete=models.CASCADE,
                               related_name='mensajes')

    # Indica si el mensaje es del usuario o del bot
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)

    # Contenido del mensaje
    contenido = models.TextField()

    # Intención detectada por el bot en el mensaje
    intencion = models.CharField(max_length=100, blank=True, null=True)

    # Confianza del modelo al detectar la intención (0 a 1)
    confianza = models.FloatField(blank=True, null=True)

    fecha_envio = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Mensaje de Chat'
        verbose_name_plural = 'Mensajes de Chat'
        ordering = ['fecha_envio']

    def __str__(self):
        return f'{self.tipo}: {self.contenido[:50]}'


class IntenciónBot(models.Model):
    # Nombre único de la intención
    nombre = models.CharField(max_length=100, unique=True)

    # Descripción de qué hace esta intención
    descripcion = models.TextField(blank=True, null=True)

    # Palabras clave que activan esta intención
    palabras_clave = models.JSONField(default=list)

    # Respuesta predeterminada del bot para esta intención
    respuesta_base = models.TextField()

    # Indica si esta intención está activa
    activo = models.BooleanField(default=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Intención del Bot'
        verbose_name_plural = 'Intenciones del Bot'

    def __str__(self):
        return self.nombre


class RespuestaRapida(models.Model):
    # Intención a la que pertenece esta respuesta rápida
    intencion = models.ForeignKey(IntenciónBot, on_delete=models.CASCADE,
                                related_name='respuestas_rapidas')

    # Texto del botón de respuesta rápida
    texto = models.CharField(max_length=100)

    # Valor que se envía al seleccionar esta respuesta
    valor = models.CharField(max_length=100)

    # Orden de aparición del botón
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = 'Respuesta Rápida'
        verbose_name_plural = 'Respuestas Rápidas'
        ordering = ['orden']

    def __str__(self):
        return f'{self.intencion} - {self.texto}'