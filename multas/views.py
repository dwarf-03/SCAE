from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Multa, PagoMulta, ConfiguracionMulta

@login_required
def lista(request):
    # Obtiene todas las multas ordenadas por fecha
    multas = Multa.objects.select_related(
        'alquiler', 'cliente__usuario').order_by('-fecha_creacion')

    # Filtros
    estado = request.GET.get('estado', '')
    if estado:
        multas = multas.filter(estado=estado)

    # Total de multas pendientes
    total_pendiente = Multa.objects.filter(
        estado='pendiente').aggregate(
        total=Sum('monto_total'))['total'] or 0

    context = {
        'multas': multas,
        'estado': estado,
        'total_pendiente': total_pendiente,
        'total': multas.count(),
    }
    return render(request, 'multas/lista.html', context)


@login_required
def detalle(request, pk):
    # Muestra el detalle de una multa
    multa = get_object_or_404(Multa, pk=pk)
    pagos = multa.pagos.all()

    context = {
        'multa': multa,
        'pagos': pagos,
    }
    return render(request, 'multas/detalle.html', context)


@login_required
def pagar(request, pk):
    multa = get_object_or_404(Multa, pk=pk, estado='pendiente')

    if request.method == 'POST':
        try:
            monto = request.POST.get('monto')
            metodo_pago = request.POST.get('metodo_pago')
            referencia = request.POST.get('referencia')

            # Registra el pago
            PagoMulta.objects.create(
                multa=multa,
                monto=monto,
                metodo_pago=metodo_pago,
                referencia=referencia,
                registrado_por=request.user,
            )

            # Marca la multa como pagada
            multa.estado = 'pagada'
            multa.save()

            # Actualiza deuda del cliente
            cliente = multa.cliente
            multas_pendientes = Multa.objects.filter(
                cliente=cliente, estado='pendiente'
            ).aggregate(total=Sum('monto_total'))['total'] or 0

            cliente.deuda_total = multas_pendientes
            cliente.tiene_deuda = multas_pendientes > 0
            cliente.save()

            messages.success(request, 'Pago de multa registrado exitosamente.')
            return redirect('multas:lista')
        except Exception as e:
            messages.error(request, f'Error al registrar pago: {str(e)}')

    return render(request, 'multas/pagar.html', {'multa': multa})


@login_required
def condonar(request, pk):
    multa = get_object_or_404(Multa, pk=pk, estado='pendiente')

    if request.method == 'POST':
        motivo = request.POST.get('motivo')
        # Condona la multa con el motivo indicado
        multa.estado = 'condonada'
        multa.motivo_condonacion = motivo
        multa.save()

        # Actualiza deuda del cliente
        cliente = multa.cliente
        multas_pendientes = Multa.objects.filter(
            cliente=cliente, estado='pendiente'
        ).aggregate(total=Sum('monto_total'))['total'] or 0

        cliente.deuda_total = multas_pendientes
        cliente.tiene_deuda = multas_pendientes > 0
        cliente.save()

        messages.success(request, 'Multa condonada exitosamente.')
        return redirect('multas:lista')

    return render(request, 'multas/condonar.html', {'multa': multa})


@login_required
def configuracion(request):
    # Obtiene la configuración activa o crea una por defecto
    config = ConfiguracionMulta.objects.filter(activo=True).first()

    if request.method == 'POST':
        try:
            valor_dia = request.POST.get('valor_por_dia')
            dias_gracia = request.POST.get('dias_gracia')
            porcentaje = request.POST.get('porcentaje_adicional', 0)

            if config:
                # Actualiza configuración existente
                config.valor_por_dia = valor_dia
                config.dias_gracia = dias_gracia
                config.porcentaje_adicional = porcentaje
                config.save()
            else:
                # Crea nueva configuración
                ConfiguracionMulta.objects.create(
                    valor_por_dia=valor_dia,
                    dias_gracia=dias_gracia,
                    porcentaje_adicional=porcentaje,
                )
            messages.success(request, 'Configuración actualizada exitosamente.')
            return redirect('multas:configuracion')
        except Exception as e:
            messages.error(request, f'Error al guardar configuración: {str(e)}')

    return render(request, 'multas/configuracion.html', {'config': config})