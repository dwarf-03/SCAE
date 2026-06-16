from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from .models import Auditoria
from inventario.models import Herramienta
from alquileres.models import Alquiler
from clientes.models import Cliente
from multas.models import Multa
from devoluciones.models import Devolucion


# Registra login
@receiver(user_logged_in)
def log_login(sender, request, user, **kwargs):
    Auditoria.registrar(
        usuario=user,
        accion='login',
        modulo='usuarios',
        descripcion=f'El usuario {user.username} inició sesión',
        ip_address=request.META.get('REMOTE_ADDR'),
    )


# Registra logout
@receiver(user_logged_out)
def log_logout(sender, request, user, **kwargs):
    if user:
        Auditoria.registrar(
            usuario=user,
            accion='logout',
            modulo='usuarios',
            descripcion=f'El usuario {user.username} cerró sesión',
            ip_address=request.META.get('REMOTE_ADDR'),
        )


# Registra cambios en herramientas
@receiver(post_save, sender=Herramienta)
def log_herramienta(sender, instance, created, **kwargs):
    accion = 'crear' if created else 'editar'
    descripcion = f'{"Creó" if created else "Editó"} herramienta: {instance.nombre} ({instance.codigo})'
    Auditoria.registrar(
        usuario=None,
        accion=accion,
        modulo='inventario',
        registro_id=instance.pk,
        descripcion=descripcion,
    )


# Registra cambios en alquileres
@receiver(post_save, sender=Alquiler)
def log_alquiler(sender, instance, created, **kwargs):
    accion = 'crear' if created else 'editar'
    descripcion = f'{"Creó" if created else "Editó"} alquiler: {instance.numero}'
    Auditoria.registrar(
        usuario=None,
        accion=accion,
        modulo='alquileres',
        registro_id=instance.pk,
        descripcion=descripcion,
    )


# Registra cambios en clientes
@receiver(post_save, sender=Cliente)
def log_cliente(sender, instance, created, **kwargs):
    accion = 'crear' if created else 'editar'
    descripcion = f'{"Creó" if created else "Editó"} cliente: {instance.nombre_completo}'
    Auditoria.registrar(
        usuario=None,
        accion=accion,
        modulo='clientes',
        registro_id=instance.pk,
        descripcion=descripcion,
    )


# Registra multas
@receiver(post_save, sender=Multa)
def log_multa(sender, instance, created, **kwargs):
    if created:
        Auditoria.registrar(
            usuario=None,
            accion='crear',
            modulo='multas',
            registro_id=instance.pk,
            descripcion=f'Multa generada para alquiler {instance.alquiler.numero} - ${instance.monto_total}',
        )


# Registra devoluciones
@receiver(post_save, sender=Devolucion)
def log_devolucion(sender, instance, created, **kwargs):
    if created:
        Auditoria.registrar(
            usuario=None,
            accion='crear',
            modulo='devoluciones',
            registro_id=instance.pk,
            descripcion=f'Devolución registrada para alquiler {instance.alquiler.numero}',
        )