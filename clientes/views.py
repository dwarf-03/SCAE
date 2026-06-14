from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cliente, DocumentoCliente
from usuarios.models import Usuario

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