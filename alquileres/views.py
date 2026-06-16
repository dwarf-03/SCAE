from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Alquiler, DetalleAlquiler, Reserva
from clientes.models import Cliente
from inventario.models import Herramienta
from datetime import datetime
from notificaciones.services import notificar_alquiler_confirmado


@login_required
def lista(request):
    # Obtiene todos los alquileres ordenados por fecha
    alquileres = Alquiler.objects.select_related(
        'cliente__usuario').order_by('-fecha_creacion')

    # Filtros de búsqueda
    buscar = request.GET.get('buscar', '')
    estado = request.GET.get('estado', '')

    if buscar:
        alquileres = alquileres.filter(numero__icontains=buscar) | \
                    alquileres.filter(cliente__usuario__first_name__icontains=buscar)
    if estado:
        alquileres = alquileres.filter(estado=estado)

    context = {
        'alquileres': alquileres,
        'buscar': buscar,
        'estado': estado,
        'total': alquileres.count(),
    }
    return render(request, 'alquileres/lista.html', context)


@login_required
def crear(request):
    clientes = Cliente.objects.select_related('usuario').all()
    herramientas = Herramienta.objects.filter(
        activo=True, cantidad_disponible__gt=0)

    if request.method == 'POST':
        print("POST DATA:", request.POST)
        try:
            cliente_id = request.POST.get('cliente')
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            observaciones = request.POST.get('observaciones')

            fecha_inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            hoy = timezone.now().date()
            if fecha_inicio_date < hoy:
                messages.error(request, 'La fecha de inicio no puede ser anterior a hoy.')
                return redirect('alquileres:crear')

            if fecha_fin_date <= fecha_inicio_date:
                messages.error(request, 'La fecha de devolución debe ser posterior a la fecha de inicio.')
                return redirect('alquileres:crear')

            dias = (fecha_fin_date - fecha_inicio_date).days

            alquiler = Alquiler.objects.create(
                cliente_id=cliente_id,
                registrado_por=request.user,
                fecha_inicio=fecha_inicio_date,
                fecha_fin=fecha_fin_date,
                estado='activo',
                canal='web',
                observaciones=observaciones,
            )

            herramienta_ids = request.POST.getlist('herramienta_id')
            cantidades = request.POST.getlist('cantidad')

            subtotal = 0
            for h_id, cantidad in zip(herramienta_ids, cantidades):
                cantidad = int(cantidad)
                herramienta = Herramienta.objects.get(pk=h_id)
                precio = herramienta.precio_diario
                sub = precio * cantidad * dias

                DetalleAlquiler.objects.create(
                    alquiler=alquiler,
                    herramienta=herramienta,
                    cantidad=cantidad,
                    precio_diario=precio,
                    subtotal=sub,
                )

                herramienta.cantidad_disponible -= cantidad
                herramienta.cantidad_alquilada += cantidad
                herramienta.actualizar_estado()
                subtotal += sub

            alquiler.subtotal = subtotal
            alquiler.total = subtotal
            alquiler.save()

            # 🔔 Notificar al cliente por WhatsApp
            try:
                notificar_alquiler_confirmado(alquiler)
            except Exception as e:
                print("ERROR NOTIFICACION:", e)  # temporal para debug

            messages.success(request, f'Alquiler {alquiler.numero} creado exitosamente.')
            return redirect('alquileres:detalle', pk=alquiler.pk)

        except Exception as e:
            messages.error(request, f'Error al crear alquiler: {str(e)}')

    context = {
        'clientes': clientes,
        'herramientas': herramientas,
        'hoy': timezone.now().date(),
    }
    return render(request, 'alquileres/crear.html', context)


@login_required
def detalle(request, pk):
    # Muestra el detalle completo del alquiler
    alquiler = get_object_or_404(Alquiler, pk=pk)
    detalles = alquiler.detalles.select_related('herramienta').all()

    context = {
        'alquiler': alquiler,
        'detalles': detalles,
    }
    return render(request, 'alquileres/detalle.html', context)


@login_required
def cancelar(request, pk):
    alquiler = get_object_or_404(Alquiler, pk=pk)
    if request.method == 'POST':
        # Cancela el alquiler y devuelve inventario
        for detalle in alquiler.detalles.all():
            herramienta = detalle.herramienta
            herramienta.cantidad_disponible += detalle.cantidad
            herramienta.cantidad_alquilada -= detalle.cantidad
            herramienta.actualizar_estado()

        alquiler.estado = 'cancelado'
        alquiler.save()
        messages.success(request, f'Alquiler {alquiler.numero} cancelado.')
        return redirect('alquileres:lista')
    return render(request, 'alquileres/cancelar.html', {'alquiler': alquiler})


    