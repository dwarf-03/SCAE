from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Auditoria

@login_required
def lista(request):
    # Obtiene todas las auditorías ordenadas por fecha
    auditorias = Auditoria.objects.select_related('usuario').order_by('-fecha_accion')

    # Filtros
    accion = request.GET.get('accion', '')
    modulo = request.GET.get('modulo', '')
    usuario = request.GET.get('usuario', '')
    fecha_inicio = request.GET.get('fecha_inicio', '')
    fecha_fin = request.GET.get('fecha_fin', '')

    if accion:
        auditorias = auditorias.filter(accion=accion)
    if modulo:
        auditorias = auditorias.filter(modulo__icontains=modulo)
    if usuario:
        auditorias = auditorias.filter(usuario__username__icontains=usuario)
    if fecha_inicio:
        auditorias = auditorias.filter(fecha_accion__date__gte=fecha_inicio)
    if fecha_fin:
        auditorias = auditorias.filter(fecha_accion__date__lte=fecha_fin)

    context = {
        'auditorias': auditorias[:100],
        'total': auditorias.count(),
        'accion': accion,
        'modulo': modulo,
        'usuario': usuario,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    }
    return render(request, 'auditoria/lista.html', context)