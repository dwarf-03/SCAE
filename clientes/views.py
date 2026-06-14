from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, DocumentoCliente
from usuarios.models import Usuario
from django.utils import timezone

@login_required
def lista(request):
    # Obtiene todos los clientes con su usuario relacionado
    clientes = Cliente.objects.select_related('usuario').all()

    # Filtros de búsqueda
    buscar = request.GET.get('buscar', '')
    verificado = request.GET.get('verificado', '')

    if buscar:
        clientes = clientes.filter(
            usuario__first_name__icontains=buscar
        ) | clientes.filter(
            usuario__last_name__icontains=buscar
        ) | clientes.filter(
            numero_documento__icontains=buscar
        )
    if verificado:
        clientes = clientes.filter(verificado=verificado == 'true')

    context = {
        'clientes': clientes,
        'buscar': buscar,
        'verificado': verificado,
        'total': clientes.count(),
    }
    return render(request, 'clientes/lista.html', context)


@login_required
def crear(request):
    if request.method == 'POST':
        try:
            # Crea el usuario del sistema primero
            usuario = Usuario.objects.create_user(
                username=request.POST.get('username'),
                email=request.POST.get('email'),
                password=request.POST.get('password'),
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                rol='cliente',
            )

            # Crea el perfil del cliente
            cliente = Cliente.objects.create(
                usuario=usuario,
                tipo_documento=request.POST.get('tipo_documento'),
                numero_documento=request.POST.get('numero_documento'),
                telefono=request.POST.get('telefono'),
                telefono_alternativo=request.POST.get('telefono_alternativo'),
                direccion=request.POST.get('direccion'),
                ciudad=request.POST.get('ciudad'),
                notas=request.POST.get('notas'),
            )

            # Guarda foto del documento si se subió
            if 'foto_documento' in request.FILES:
                cliente.foto_documento = request.FILES['foto_documento']
                cliente.save()

            messages.success(request, f'Cliente {usuario.get_full_name()} creado exitosamente.')
            return redirect('clientes:lista')
        except Exception as e:
            messages.error(request, f'Error al crear cliente: {str(e)}')

    return render(request, 'clientes/crear.html')


@login_required
def detalle(request, pk):
    # Muestra el detalle completo del cliente con su historial
    cliente = get_object_or_404(Cliente, pk=pk)
    alquileres = cliente.alquileres.all().order_by('-fecha_creacion')[:10]
    multas = cliente.multas.all().order_by('-fecha_creacion')[:5]

    context = {
        'cliente': cliente,
        'alquileres': alquileres,
        'multas': multas,
    }
    return render(request, 'clientes/detalle.html', context)


@login_required
def editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        try:
            # Actualiza datos del usuario
            usuario = cliente.usuario
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            usuario.email = request.POST.get('email')
            usuario.save()

            # Actualiza datos del cliente
            cliente.tipo_documento = request.POST.get('tipo_documento')
            cliente.numero_documento = request.POST.get('numero_documento')
            cliente.telefono = request.POST.get('telefono')
            cliente.telefono_alternativo = request.POST.get('telefono_alternativo')
            cliente.direccion = request.POST.get('direccion')
            cliente.ciudad = request.POST.get('ciudad')
            cliente.verificado = request.POST.get('verificado') == 'on'
            cliente.notas = request.POST.get('notas')

            if 'foto_documento' in request.FILES:
                cliente.foto_documento = request.FILES['foto_documento']

            cliente.save()
            messages.success(request, f'Cliente {cliente.nombre_completo} actualizado.')
            return redirect('clientes:lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')

    return render(request, 'clientes/editar.html', {'cliente': cliente})


@login_required
def eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        # Desactiva el usuario en lugar de eliminar
        cliente.usuario.activo = False
        cliente.usuario.save()
        messages.success(request, f'Cliente {cliente.nombre_completo} eliminado.')
        return redirect('clientes:lista')
    return render(request, 'clientes/eliminar.html', {'cliente': cliente})

@login_required
def mi_perfil(request):
    # Vista exclusiva para el cliente logueado
    try:
        cliente = Cliente.objects.get(usuario=request.user)
        alquileres = cliente.alquileres.all().order_by('-fecha_creacion')
        multas = cliente.multas.filter(estado='pendiente')

        context = {
            'cliente': cliente,
            'alquileres': alquileres,
            'multas': multas,
        }
        return render(request, 'clientes/mi_perfil.html', context)
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes perfil de cliente asignado.')
        return redirect('login')


@login_required
def solicitar_alquiler(request):
    from inventario.models import Herramienta
    from alquileres.models import Alquiler, DetalleAlquiler
    from datetime import datetime

    # El cliente solicita un alquiler desde su panel
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, 'No tienes perfil de cliente asignado.')
        return redirect('login')

    herramientas = Herramienta.objects.filter(activo=True, cantidad_disponible__gt=0)
    hoy = timezone.now().date()

    if request.method == 'POST':
        try:
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            fecha_inicio_date = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            fecha_fin_date = datetime.strptime(fecha_fin, '%Y-%m-%d').date()

            # Valida fechas
            if fecha_inicio_date < hoy:
                messages.error(request, 'La fecha de inicio no puede ser anterior a hoy.')
                return redirect('clientes:solicitar_alquiler')

            if fecha_fin_date <= fecha_inicio_date:
                messages.error(request, 'La fecha de devolución debe ser posterior al inicio.')
                return redirect('clientes:solicitar_alquiler')

            # Crea el alquiler
            alquiler = Alquiler.objects.create(
                cliente=cliente,
                registrado_por=request.user,
                fecha_inicio=fecha_inicio_date,
                fecha_fin=fecha_fin_date,
                estado='activo',
                canal='web',
                observaciones=request.POST.get('observaciones'),
            )

            # Procesa herramientas
            herramienta_ids = request.POST.getlist('herramienta_id')
            cantidades = request.POST.getlist('cantidad')
            dias = (fecha_fin_date - fecha_inicio_date).days
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

                # Descuenta inventario
                herramienta.cantidad_disponible -= cantidad
                herramienta.cantidad_alquilada += cantidad
                herramienta.save()

            alquiler.subtotal = subtotal
            alquiler.total = subtotal
            alquiler.save()

            messages.success(request, f'Alquiler {alquiler.numero} creado exitosamente.')
            return redirect('clientes:mi_perfil')

        except Exception as e:
            messages.error(request, f'Error al crear alquiler: {str(e)}')

    context = {
        'herramientas': herramientas,
        'hoy': hoy,
        'cliente': cliente,
    }
    return render(request, 'clientes/solicitar_alquiler.html', context)

@login_required
def mis_alquileres(request):
    # Lista todos los alquileres del cliente logueado
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('login')

    alquileres = cliente.alquileres.all().order_by('-fecha_creacion')
    return render(request, 'clientes/mis_alquileres.html', {
        'alquileres': alquileres,
        'cliente': cliente,
    })


@login_required
def mis_multas(request):
    # Lista todas las multas del cliente logueado
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('login')

    multas = cliente.multas.all().order_by('-fecha_creacion')
    return render(request, 'clientes/mis_multas.html', {
        'multas': multas,
        'cliente': cliente,
    })


@login_required
def mis_devoluciones(request):
    # Lista todas las devoluciones del cliente logueado
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('login')

    from devoluciones.models import Devolucion
    devoluciones = Devolucion.objects.filter(
        alquiler__cliente=cliente).order_by('-fecha_creacion')
    return render(request, 'clientes/mis_devoluciones.html', {
        'devoluciones': devoluciones,
        'cliente': cliente,
    })


@login_required
def mi_alquiler_detalle(request, pk):
    # Detalle de un alquiler específico del cliente
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('login')

    from alquileres.models import Alquiler
    alquiler = get_object_or_404(Alquiler, pk=pk, cliente=cliente)
    detalles = alquiler.detalles.select_related('herramienta').all()
    return render(request, 'clientes/mi_alquiler_detalle.html', {
        'alquiler': alquiler,
        'detalles': detalles,
        'cliente': cliente,
    })


@login_required
def editar_perfil(request):
    # El cliente edita su propio perfil
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        try:
            usuario = cliente.usuario
            usuario.first_name = request.POST.get('first_name')
            usuario.last_name = request.POST.get('last_name')
            usuario.email = request.POST.get('email')
            usuario.save()

            cliente.telefono = request.POST.get('telefono')
            cliente.telefono_alternativo = request.POST.get('telefono_alternativo')
            cliente.direccion = request.POST.get('direccion')
            cliente.ciudad = request.POST.get('ciudad')
            cliente.save()

            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('clientes:mi_perfil')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')

    return render(request, 'clientes/editar_perfil.html', {'cliente': cliente})


@login_required
def cambiar_password(request):
    # El cliente cambia su contraseña
    if request.method == 'POST':
        password_actual = request.POST.get('password_actual')
        password_nuevo = request.POST.get('password_nuevo')
        password_confirmar = request.POST.get('password_confirmar')

        # Verifica contraseña actual
        from django.contrib.auth import authenticate
        user = authenticate(request, username=request.user.username, password=password_actual)

        if user is None:
            messages.error(request, 'La contraseña actual es incorrecta.')
        elif password_nuevo != password_confirmar:
            messages.error(request, 'Las contraseñas nuevas no coinciden.')
        elif len(password_nuevo) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
        else:
            request.user.set_password(password_nuevo)
            request.user.save()
            messages.success(request, 'Contraseña actualizada. Inicia sesión de nuevo.')
            return redirect('login')

    return render(request, 'clientes/cambiar_password.html')