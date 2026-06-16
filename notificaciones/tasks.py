from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from alquileres.models import Alquiler
from .services import notificar_recordatorio


@shared_task
def enviar_recordatorios():
    """
    Tarea que se ejecuta diariamente para enviar recordatorios
    de alquileres próximos a vencer.
    """
    hoy = timezone.now().date()

    for dias in [3, 1]:
        fecha_objetivo = hoy + timedelta(days=dias)

        alquileres = Alquiler.objects.filter(
            fecha_fin=fecha_objetivo,
            estado='activo',
        )

        for alquiler in alquileres:
            try:
                notificar_recordatorio(alquiler, dias)
            except Exception as e:
                print(f'Error enviando recordatorio alquiler {alquiler.id}: {e}')