from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import DetalleAlquiler, Alquiler

# Guarda el estado anterior antes de guardar
@receiver(pre_save, sender=Alquiler)
def guardar_estado_anterior(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._estado_anterior = Alquiler.objects.get(pk=instance.pk).estado
        except Alquiler.DoesNotExist:
            instance._estado_anterior = None
    else:
        instance._estado_anterior = None


@receiver(post_save, sender=DetalleAlquiler)
def descontar_stock_al_crear(sender, instance, created, **kwargs):
    if created:
        herramienta = instance.herramienta
        herramienta.cantidad_disponible -= instance.cantidad
        herramienta.cantidad_alquilada += instance.cantidad
        herramienta.cantidad_disponible = max(0, herramienta.cantidad_disponible)
        herramienta.save()
        herramienta.actualizar_estado()


@receiver(post_save, sender=Alquiler)
def restaurar_stock_al_devolver(sender, instance, **kwargs):
    estado_anterior = getattr(instance, '_estado_anterior', None)
    estados_finales = ['devuelto', 'cancelado']

    # Solo actúa si cambió A un estado final desde un estado activo
    if instance.estado in estados_finales and estado_anterior not in estados_finales:
        for detalle in instance.detalles.all():
            herramienta = detalle.herramienta
            herramienta.cantidad_disponible += detalle.cantidad
            herramienta.cantidad_alquilada -= detalle.cantidad
            herramienta.cantidad_alquilada = max(0, herramienta.cantidad_alquilada)
            herramienta.cantidad_disponible = min(
                herramienta.cantidad_disponible,
                herramienta.cantidad_total
            )
            herramienta.save()
            herramienta.actualizar_estado()