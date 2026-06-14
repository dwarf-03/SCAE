from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from .models import Devolucion, DetalleDevolucion
from alquileres.models import Alquiler
from multas.models import Multa, ConfiguracionMulta
from inventario.models import Herramienta
from django.db import models


@login_required
def lista(request):
    # Obtiene todas las devoluciones ordenadas por fecha
    devoluciones = Devolucion.objects.select_related(
        'alquiler__cliente__usuario').order_by('-fecha_creacion')

    # Obtiene alquileres activos pendientes de devolución
    alquileres_activos = Alquiler.objects.filter(
        estado='activo').select_related('cliente__usuario').order_by('fecha_fin')

    context = {
        'devoluciones': devoluciones,
        'alquileres_activos': alquileres_activos,
        'total': devoluciones.count(),
    }
    return render(request, 'devoluciones/lista.html', context)


@login_required
def recibir(request, pk):
    # Obtiene el alquiler activo a devolver
    alquiler = get_object_or_404(Alquiler, pk=pk, estado='activo')

    if request.method == 'POST':
        try:
            fecha_devolucion = request.POST.get('fecha_devolucion')
            fecha_devolucion_date = datetime.strptime(fecha_devolucion, '%Y-%m-%d').date()
            observaciones = request.POST.get('observaciones')
            estado = request.POST.get('estado')

            # Calcula si hay retraso
            dias_retraso = 0
            tiene_multa = False
            if fecha_devolucion_date > alquiler.fecha_fin:
                dias_retraso = (fecha_devolucion_date - alquiler.fecha_fin).days
                tiene_multa = True

            # Crea la devolución
            devolucion = Devolucion.objects.create(
                alquiler=alquiler,
                recibido_por=request.user,
                fecha_devolucion=fecha_devolucion_date,
                estado=estado,
                tiene_multa=tiene_multa,
                observaciones=observaciones,
            )

            # Procesa cada herramienta y actualiza inventario
            for detalle in alquiler.detalles.all():
                condicion = request.POST.get(f'condicion_{detalle.pk}', 'bueno')
                costo_dano = request.POST.get(f'costo_dano_{detalle.pk}', 0)
                descripcion_dano = request.POST.get(f'descripcion_dano_{detalle.pk}', '')

                DetalleDevolucion.objects.create(
                    devolucion=devolucion,
                    detalle_alquiler=detalle,
                    cantidad_devuelta=detalle.cantidad,
                    condicion=condicion,
                    costo_dano=costo_dano or 0,
                    descripcion_dano=descripcion_dano,
                )

                # Actualiza inventario directamente en BD
                Herramienta.objects.filter(pk=detalle.herramienta.pk).update(
                    cantidad_disponible=models.F('cantidad_disponible') + detalle.cantidad,
                    cantidad_alquilada=models.Case(
                        models.When(
                            cantidad_alquilada__gte=detalle.cantidad,
                            then=models.F('cantidad_alquilada') - detalle.cantidad
                        ),
                        default=0,
                        output_field=models.PositiveIntegerField()
                    )
                )

            # Actualiza estado del alquiler
            alquiler.estado = 'devuelto'
            alquiler.fecha_devolucion_real = fecha_devolucion_date
            alquiler.save()

            # Genera multa si hay retraso
            if tiene_multa:
                config = ConfiguracionMulta.objects.filter(activo=True).first()
                valor_dia = config.valor_por_dia if config else 50000
                dias_con_gracia = max(0, dias_retraso - (config.dias_gracia if config else 0))

                if dias_con_gracia > 0:
                    Multa.objects.create(
                        alquiler=alquiler,
                        cliente=alquiler.cliente,
                        fecha_vencimiento=alquiler.fecha_fin,
                        fecha_devolucion=fecha_devolucion_date,
                        dias_retraso=dias_con_gracia,
                        valor_por_dia=valor_dia,
                        monto_total=valor_dia * dias_con_gracia,
                        registrado_por=request.user,
                    )
                    messages.warning(request, f'Se generó una multa por {dias_con_gracia} días de retraso.')

            messages.success(request, 'Devolución registrada exitosamente.')
            return redirect('devoluciones:lista')

        except Exception as e:
            messages.error(request, f'Error al registrar devolución: {str(e)}')

    context = {
        'alquiler': alquiler,
        'detalles': alquiler.detalles.select_related('herramienta').all(),
        'hoy': timezone.now().date(),
    }
    return render(request, 'devoluciones/recibir.html', context)


@login_required
def detalle(request, pk):
    # Muestra el detalle de una devolución
    devolucion = get_object_or_404(Devolucion, pk=pk)
    detalles = devolucion.detalles.select_related(
        'detalle_alquiler__herramienta').all()

    context = {
        'devolucion': devolucion,
        'detalles': detalles,
    }
    return render(request, 'devoluciones/detalle.html', context)