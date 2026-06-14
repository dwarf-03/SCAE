from django.db import models
from alquileres.models import Alquiler, DetalleAlquiler
from usuarios.models import Usuario

class Devolucion(models.Model):
    ESTADO_CHOICES = [
        ('completa', 'Completa'),
        ('parcial', 'Parcial'),
        ('con_danos', 'Con Daños'),
    ]

    # Alquiler al que pertenece esta devolución
    alquiler = models.ForeignKey(Alquiler, on_delete=models.PROTECT, related_name='devoluciones')

    # Empleado que recibió la devolución
    recibido_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='devoluciones_recibidas')

    # Fecha real en que se realizó la devolución
    fecha_devolucion = models.DateField()

    # Estado general de la devolución
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='completa')

    # Indica si se generó multa por retraso
    tiene_multa = models.BooleanField(default=False)

    # Observaciones generales de la devolución
    observaciones = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Devolución'
        verbose_name_plural = 'Devoluciones'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Devolución {self.alquiler.numero} - {self.fecha_devolucion}'

    @property
    def dias_retraso(self):
        # Calcula días de retraso comparando fecha real vs fecha pactada
        if self.fecha_devolucion > self.alquiler.fecha_fin:
            return (self.fecha_devolucion - self.alquiler.fecha_fin).days
        return 0

    @property
    def fue_a_tiempo(self):
        # Verifica si la devolución fue antes o en la fecha pactada
        return self.fecha_devolucion <= self.alquiler.fecha_fin


class DetalleDevolucion(models.Model):
    CONDICION_CHOICES = [
        ('bueno', 'Bueno'),
        ('regular', 'Regular'),
        ('danado', 'Dañado'),
        ('perdido', 'Perdido'),
    ]

    # Devolución a la que pertenece este detalle
    devolucion = models.ForeignKey(Devolucion, on_delete=models.CASCADE, related_name='detalles')

    # Detalle del alquiler que se está devolviendo
    detalle_alquiler = models.ForeignKey(DetalleAlquiler, on_delete=models.PROTECT, related_name='devoluciones')

    # Cantidad de unidades devueltas
    cantidad_devuelta = models.PositiveIntegerField(default=1)

    # Condición en que se devuelve la herramienta
    condicion = models.CharField(max_length=20, choices=CONDICION_CHOICES, default='bueno')

    # Costo adicional por daños si aplica
    costo_dano = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Descripción del daño encontrado
    descripcion_dano = models.TextField(blank=True, null=True)

    # Fotografía del estado de la herramienta al devolver
    foto_evidencia = models.ImageField(upload_to='devoluciones/', blank=True, null=True)

    class Meta:
        verbose_name = 'Detalle de Devolución'
        verbose_name_plural = 'Detalles de Devolución'

    def __str__(self):
        return f'{self.devolucion} - {self.detalle_alquiler.herramienta.nombre}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Actualiza el inventario al guardar el detalle de devolución
        self._actualizar_inventario()

    def _actualizar_inventario(self):
    # Actualiza inventario directamente en BD sin llamar actualizar_estado
        from inventario.models import Herramienta
        from django.db import models as db_models
        herramienta = self.detalle_alquiler.herramienta
        Herramienta.objects.filter(pk=herramienta.pk).update(
        cantidad_disponible=db_models.F('cantidad_disponible') + self.cantidad_devuelta,
        cantidad_alquilada=db_models.Case(
            db_models.When(
                cantidad_alquilada__gte=self.cantidad_devuelta,
                then=db_models.F('cantidad_alquilada') - self.cantidad_devuelta
            ),
            default=0,
            output_field=db_models.PositiveIntegerField()
        )
    )