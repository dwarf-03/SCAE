from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Herramienta, Categoria

@login_required
def lista(request):
    # Obtiene todas las herramientas activas
    herramientas = Herramienta.objects.filter(activo=True).select_related('categoria')
    categorias = Categoria.objects.filter(activo=True)

    # Filtros de búsqueda
    buscar = request.GET.get('buscar', '')
    categoria_id = request.GET.get('categoria', '')
    estado = request.GET.get('estado', '')

    if buscar:
        herramientas = herramientas.filter(nombre__icontains=buscar)
    if categoria_id:
        herramientas = herramientas.filter(categoria_id=categoria_id)
    if estado:
        herramientas = herramientas.filter(estado=estado)

    context = {
        'herramientas': herramientas,
        'categorias': categorias,
        'buscar': buscar,
        'categoria_id': categoria_id,
        'estado': estado,
        'total': herramientas.count(),
    }
    return render(request, 'inventario/lista.html', context)


@login_required
def crear(request):
    categorias = Categoria.objects.filter(activo=True)

    if request.method == 'POST':
        try:
            # Crea la herramienta con los datos del formulario
            herramienta = Herramienta.objects.create(
                codigo=request.POST.get('codigo'),
                nombre=request.POST.get('nombre'),
                categoria_id=request.POST.get('categoria'),
                descripcion=request.POST.get('descripcion'),
                precio_diario=request.POST.get('precio_diario'),
                cantidad_total=request.POST.get('cantidad_total'),
                cantidad_disponible=request.POST.get('cantidad_total'),
                estado='disponible',
            )
            # Guarda la fotografía si se subió
            if 'fotografia' in request.FILES:
                herramienta.fotografia = request.FILES['fotografia']
                herramienta.save()

            # Genera el código QR automáticamente
            herramienta.generar_qr()

            messages.success(request, f'Herramienta {herramienta.nombre} creada exitosamente.')
            return redirect('inventario:lista')
        except Exception as e:
            messages.error(request, f'Error al crear herramienta: {str(e)}')

    return render(request, 'inventario/crear.html', {'categorias': categorias})


@login_required
def editar(request, pk):
    # Obtiene la herramienta o retorna 404
    herramienta = get_object_or_404(Herramienta, pk=pk)
    categorias = Categoria.objects.filter(activo=True)

    if request.method == 'POST':
        try:
            herramienta.codigo = request.POST.get('codigo')
            herramienta.nombre = request.POST.get('nombre')
            herramienta.categoria_id = request.POST.get('categoria')
            herramienta.descripcion = request.POST.get('descripcion')
            herramienta.precio_diario = request.POST.get('precio_diario')
            herramienta.estado = request.POST.get('estado')

            if 'fotografia' in request.FILES:
                herramienta.fotografia = request.FILES['fotografia']

            herramienta.save()
            messages.success(request, f'Herramienta {herramienta.nombre} actualizada.')
            return redirect('inventario:lista')
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')

    context = {
        'herramienta': herramienta,
        'categorias': categorias,
    }
    return render(request, 'inventario/editar.html', context)


@login_required
def detalle(request, pk):
    # Muestra el detalle completo de una herramienta
    herramienta = get_object_or_404(Herramienta, pk=pk)
    return render(request, 'inventario/detalle.html', {'herramienta': herramienta})


@login_required
def eliminar(request, pk):
    herramienta = get_object_or_404(Herramienta, pk=pk)
    if request.method == 'POST':
        # Desactiva la herramienta en lugar de eliminarla
        herramienta.activo = False
        herramienta.save()
        messages.success(request, f'Herramienta {herramienta.nombre} eliminada.')
        return redirect('inventario:lista')
    return render(request, 'inventario/eliminar.html', {'herramienta': herramienta})


@login_required
def categorias(request):
    # Lista todas las categorías
    lista_categorias = Categoria.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        if nombre:
            Categoria.objects.create(nombre=nombre, descripcion=descripcion)
            messages.success(request, f'Categoría {nombre} creada.')
            return redirect('inventario:categorias')

    return render(request, 'inventario/categorias.html', {'categorias': lista_categorias})