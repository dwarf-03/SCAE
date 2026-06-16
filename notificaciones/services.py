from twilio.rest import Client
from django.conf import settings
from .models import Notificacion, PlantillaNotificacion
from django.utils import timezone


def enviar_whatsapp(cliente, tipo_plantilla, contexto):
    try:
        plantilla = PlantillaNotificacion.objects.get(
            tipo=tipo_plantilla,
            activo=True,
            canal__in=['whatsapp', 'ambos']
        )
    except PlantillaNotificacion.DoesNotExist:
        return False, 'Plantilla no encontrada'

    mensaje = plantilla.mensaje.format(**contexto)

    notificacion = Notificacion.objects.create(
        cliente=cliente,
        plantilla=plantilla,
        canal='whatsapp',
        asunto=plantilla.asunto,
        mensaje=mensaje,
    )

    if not cliente.telefono:
        notificacion.marcar_fallida('Cliente sin número de teléfono')
        return False, 'Cliente sin número de teléfono'

    try:
        twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

        # Envía al cliente
        twilio_client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f'whatsapp:+57{cliente.telefono}',
            body=mensaje
        )

        # Envía copia al admin
        admin_numero = getattr(settings, 'ADMIN_WHATSAPP', None)
        if admin_numero:
            admin_mensaje = f"📋 *Copia Admin*\nCliente: {cliente}\n\n{mensaje}"
            twilio_client.messages.create(
                from_=settings.TWILIO_WHATSAPP_FROM,
                to=f'whatsapp:+57{admin_numero}',
                body=admin_mensaje
            )

        notificacion.marcar_enviada()
        return True, 'Enviado correctamente'

    except Exception as e:
        notificacion.marcar_fallida(str(e))
        return False, str(e)


def notificar_alquiler_confirmado(alquiler):
    contexto = {
        'nombre': alquiler.cliente.nombre_completo,
        'numero_alquiler': alquiler.numero,
        'fecha_fin': alquiler.fecha_fin.strftime('%d/%m/%Y'),
        'monto': f'{alquiler.total:,.0f}',
        'dias_restantes': alquiler.dias_alquiler,
    }
    return enviar_whatsapp(alquiler.cliente, 'confirmacion', contexto)


def notificar_devolucion(alquiler):
    contexto = {
        'nombre': alquiler.cliente.nombre_completo,
        'numero_alquiler': alquiler.numero,
        'fecha_fin': alquiler.fecha_fin.strftime('%d/%m/%Y'),
        'monto': f'{alquiler.total:,.0f}',
        'dias_restantes': 0,
    }
    return enviar_whatsapp(alquiler.cliente, 'devolucion', contexto)


def notificar_recordatorio(alquiler, dias_restantes):
    tipo = 'recordatorio_1dia' if dias_restantes == 1 else 'recordatorio_3dias'
    contexto = {
        'nombre': alquiler.cliente.nombre_completo,
        'numero_alquiler': alquiler.numero,
        'fecha_fin': alquiler.fecha_fin.strftime('%d/%m/%Y'),
        'dias_restantes': dias_restantes,
        'monto': f'{alquiler.total:,.0f}',
    }
    return enviar_whatsapp(alquiler.cliente, tipo, contexto)


def notificar_multa(multa):
    contexto = {
        'nombre': multa.alquiler.cliente.nombre_completo,
        'numero_alquiler': multa.alquiler.numero,
        'fecha_fin': multa.alquiler.fecha_fin.strftime('%d/%m/%Y'),
        'monto': f'{multa.monto_total:,.0f}',
        'dias_restantes': 0,
    }
    return enviar_whatsapp(multa.alquiler.cliente, 'multa', contexto)