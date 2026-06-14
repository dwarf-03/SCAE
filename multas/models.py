from django.db import models
from alquileres.models import Alquiler
from clientes.models import Cliente
from usuarios.models import Usuario

class ConfiguracionMulta(models.Model):
    # Valor cobrado por cada día de retraso
    valor_por_dia = models.DecimalField(max_digits=10, decimal_places=2, default=50000)

    # Porcentaje adicional sobre el total del alquiler por retraso
    porcentaje_adicional = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    # Días de gracia antes de aplicar multa
    dias_gracia = models.PositiveIntegerField(default=0)

    # Solo puede existir una configuración activa
    activo = models.BooleanField(default=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuración de Multa'
        verbose_name_plural = 'Configuraciones de Multas'

    def __str__(self):
        return f'Multa: ${self.valor_por_dia}/día - Gracia: {self.dias_gracia} días'


class Multa(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('pagada', 'Pagada'),
        ('condonada', 'Condonada'),
    ]

    # Alquiler que generó la multa
    alquiler = models.ForeignKey(Alquiler, on_delete=models.PROTECT, related_name='multas')

    # Cliente que debe pagar la multa
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='multas')

    # Fecha en que venció el alquiler
    fecha_vencimiento = models.DateField()

    # Fecha en que se realizó la devolución real
    fecha_devolucion = models.DateField(blank=True, null=True)

    # Días de retraso calculados
    dias_retraso = models.PositiveIntegerField(default=0)

    # Valor por día aplicado al momento de la multa
    valor_por_dia = models.DecimalField(max_digits=10, decimal_places=2)

    # Monto total de la multa
    monto_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Estado actual del pago de la multa
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')

    # Usuario que registró o gestionó la multa
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT,
                                        related_name='multas_registradas')

    # Motivo en caso de condonación
    motivo_condonacion = models.TextField(blank=True, null=True)

    # Observaciones adicionales
    observaciones = models.TextField(blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Multa'
        verbose_name_plural = 'Multas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'Multa {self.alquiler.numero} - ${self.monto_total}'

    def save(self, *args, **kwargs):
        # Calcula el monto total automáticamente antes de guardar
        self.monto_total = self.valor_por_dia * self.dias_retraso
        super().save(*args, **kwargs)

    @property
    def esta_pendiente(self):
        # Verifica si la multa aún no ha sido pagada
        return self.estado == 'pendiente'

    def calcular_multa(self):
        # Recalcula los días de retraso y el monto total
        from django.utils import timezone
        fecha_actual = timezone.now().date()
        if self.fecha_devolucion:
            self.dias_retraso = (self.fecha_devolucion - self.fecha_vencimiento).days
        else:
            self.dias_retraso = (fecha_actual - self.fecha_vencimiento).days
        self.monto_total = self.valor_por_dia * self.dias_retraso
        return self.monto_total


class PagoMulta(models.Model):
    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'),
    ]

    # Multa que se está pagando
    multa = models.ForeignKey(Multa, on_delete=models.PROTECT, related_name='pagos')

    # Monto pagado en esta transacción
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    # Método de pago utilizado
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)

    # Número de referencia del pago
    referencia = models.CharField(max_length=100, blank=True, null=True)

    # Usuario que registró el pago
    registrado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT,
                                        related_name='pagos_multas_registrados')

    # Comprobante del pago
    comprobante = models.ImageField(upload_to='pagos/multas/', blank=True, null=True)

    fecha_pago = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago de Multa'
        verbose_name_plural = 'Pagos de Multas'

    def __str__(self):
        return f'Pago {self.multa} - ${self.monto}'