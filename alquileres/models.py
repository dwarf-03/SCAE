from django.db import models
from django.core.validators import MinValueValidator
from clientes.models import Cliente
from inventario.models import Herramienta
from usuarios.models import Usuario

class Alquiler(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('vencido', 'Vencido'),
        ('devuelto', 'Devuelto'),
        ('cancelado', 'Cancelado'),
    ]

    CANAL_CHOICES = [
        ('web', 'Web'),
        ('whatsapp', 'WhatsApp'),
        ('presencial', 'Presencial'),
    ]

    # Número único de alquiler generado automáticamente
    numero = models.CharField(max_length=20, unique=True)

    # Cliente que realiza el alquiler
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='alquileres')

    # Empleado que registró el alquiler
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='alquileres_registrados')

    # Fechas del alquiler
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_devolucion_real = models.DateField(blank=True, null=True)

    # Estado actual del alquiler
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')

    # Canal por donde se realizó el alquiler
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES, default='web')

    # Costos del alquiler
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Indica si el alquiler ha sido pagado
    pagado = models.BooleanField(default=False)

    # Observaciones adicionales del alquiler
    observaciones = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Alquiler'
        verbose_name_plural = 'Alquileres'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Alquiler {self.numero} - {self.cliente}'

    def save(self, *args, **kwargs):
        # Genera número de alquiler automático si no existe
        if not self.numero:
            ultimo = Alquiler.objects.order_by('-id').first()
            siguiente = (ultimo.id + 1) if ultimo else 1
            self.numero = f'ALQ-{siguiente:05d}'
        super().save(*args, **kwargs)

    @property
    def dias_alquiler(self):
        # Calcula los días totales del alquiler
        return (self.fecha_fin - self.fecha_inicio).days

    @property
    def esta_vencido(self):
        # Verifica si el alquiler está vencido
        from django.utils import timezone
        return self.estado == 'activo' and self.fecha_fin < timezone.now().date()

    @property
    def dias_vencidos(self):
        # Calcula los días de retraso si está vencido
        from django.utils import timezone
        if self.esta_vencido:
            return (timezone.now().date() - self.fecha_fin).days
        return 0


class DetalleAlquiler(models.Model):
    # Alquiler al que pertenece este detalle
    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE, related_name='detalles')

    # Herramienta incluida en el alquiler
    herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT, related_name='detalles_alquiler')

    # Cantidad de unidades alquiladas
    cantidad = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    # Precio por día al momento del alquiler
    precio_diario = models.DecimalField(max_digits=10, decimal_places=2)

    # Total calculado para esta herramienta
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Observaciones sobre esta herramienta en el alquiler
    observaciones = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = 'Detalle de Alquiler'
        verbose_name_plural = 'Detalles de Alquiler'

    def __str__(self):
        return f'{self.alquiler.numero} - {self.herramienta.nombre}'

    def save(self, *args, **kwargs):
        # Calcula el subtotal automáticamente al guardar
        self.subtotal = self.precio_diario * self.cantidad * self.alquiler.dias_alquiler
        super().save(*args, **kwargs)


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('en_espera', 'En Lista de Espera'),
    ]

    # Cliente que realiza la reserva
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='reservas')

    # Herramienta que se desea reservar
    herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT, related_name='reservas')

    # Cantidad de unidades a reservar
    cantidad = models.PositiveIntegerField(default=1)

    # Fechas de la reserva
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    # Estado actual de la reserva
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Observaciones de la reserva
    observaciones = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Reserva {self.cliente} - {self.herramienta}'