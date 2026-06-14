from django.db import models
from usuarios.models import Usuario

class Auditoria(models.Model):
    ACCION_CHOICES = [
        ('crear', 'Crear'),
        ('editar', 'Editar'),
        ('eliminar', 'Eliminar'),
        ('login', 'Inicio de Sesión'),
        ('logout', 'Cierre de Sesión'),
        ('ver', 'Ver'),
    ]

    # Usuario que realizó la acción
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL,
                                null=True, related_name='auditorias')

    # Acción realizada en el sistema
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)

    # Módulo o modelo afectado
    modulo = models.CharField(max_length=100)

    # ID del registro afectado
    registro_id = models.PositiveIntegerField(blank=True, null=True)

    # Descripción detallada de la acción
    descripcion = models.TextField()

    # Datos anteriores al cambio en formato JSON
    datos_anteriores = models.JSONField(blank=True, null=True)

    # Datos nuevos después del cambio en formato JSON
    datos_nuevos = models.JSONField(blank=True, null=True)

    # Dirección IP desde donde se realizó la acción
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    # Navegador o cliente usado
    user_agent = models.TextField(blank=True, null=True)

    fecha_accion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha_accion']

    def __str__(self):
        return f'{self.usuario} - {self.accion} - {self.modulo} - {self.fecha_accion}'

    @classmethod
    def registrar(cls, usuario, accion, modulo, descripcion,
                registro_id=None, datos_anteriores=None,
                datos_nuevos=None, ip_address=None, user_agent=None):
        # Método de clase para registrar auditorías fácilmente desde cualquier parte
        return cls.objects.create(
            usuario=usuario,
            accion=accion,
            modulo=modulo,
            registro_id=registro_id,
            descripcion=descripcion,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos,
            ip_address=ip_address,
            user_agent=user_agent,
        )