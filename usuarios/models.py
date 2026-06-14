from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROL_CHOICES = [
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
        ('cliente', 'Cliente'),
    ]
    
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='cliente')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    documento = models.CharField(max_length=20, blank=True, null=True, unique=True)
    direccion = models.TextField(blank=True, null=True)
    foto = models.ImageField(upload_to='usuarios/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.get_full_name()} - {self.rol}'

    @property
    def es_administrador(self):
        return self.rol == 'administrador'

    @property
    def es_empleado(self):
        return self.rol == 'empleado'

    @property
    def es_cliente(self):
        return self.rol == 'cliente'