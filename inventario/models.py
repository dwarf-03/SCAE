from django.db import models
from django.core.validators import MinValueValidator
import qrcode
import os
from django.conf import settings

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Herramienta(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('rentada', 'Rentada'),
        ('reservada', 'Reservada'),
        ('mantenimiento', 'Mantenimiento'),
        ('fuera_servicio', 'Fuera de Servicio'),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='herramientas')
    descripcion = models.TextField(blank=True, null=True)
    fotografia = models.ImageField(upload_to='herramientas/', blank=True, null=True)
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)
    cantidad_alquilada = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='disponible')
    codigo_qr = models.ImageField(upload_to='qr/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Herramienta'
        verbose_name_plural = 'Herramientas'

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

    def generar_qr(self):
        # Genera el código QR de la herramienta
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(f'SCAE-{self.codigo}-{self.nombre}')
        qr.make(fit=True)
        img = qr.make_image(fill_color='black', back_color='white')
        qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', f'{self.codigo}.png')
        os.makedirs(os.path.dirname(qr_path), exist_ok=True)
        img.save(qr_path)
        self.codigo_qr = f'qr/{self.codigo}.png'
        self.save()

    def actualizar_estado(self):
        # Actualiza el estado según disponibilidad
        if self.cantidad_disponible == 0:
            self.estado = 'rentada'
        else:
            self.estado = 'disponible'
        # Guarda solo el campo estado
        Herramienta.objects.filter(pk=self.pk).update(estado=self.estado)

    @property
    def esta_disponible(self):
        # Verifica si la herramienta está disponible
        return self.cantidad_disponible > 0 and self.estado == 'disponible'