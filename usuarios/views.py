from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from alquileres.models import Alquiler
from inventario.models import Herramienta
from clientes.models import Cliente
from multas.models import Multa
from django.utils import timezone
from django.db.models import Sum
from functools import wraps
from django.http import HttpResponseForbidden



def solo_admin(view_func):
    # Permite acceso solo a administradores
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol != 'administrador':
            return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_o_empleado(view_func):
    # Permite acceso a administradores y empleados
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if request.user.rol not in ['administrador', 'empleado']:
            return HttpResponseForbidden('No tienes permisos para acceder a esta página.')
        return view_func(request, *args, **kwargs)
    return wrapper


def login_view(request):
    # Redirige al dashboard si ya está autenticado
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenido, {user.get_full_name()}')
            # Redirige según el rol del usuario
            if user.rol in ['administrador', 'empleado']:
                return redirect('dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')

    return render(request, 'usuarios/login.html')


def logout_view(request):
    # Cierra sesión y redirige al login
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente')
    return redirect('login')


@login_required
def dashboard(request):
    # Redirige a clientes a su propio panel
    if request.user.rol == 'cliente':
        return redirect('clientes:mi_perfil')

    hoy = timezone.now().date()

    # Estadísticas de inventario
    total_herramientas = Herramienta.objects.filter(activo=True).count()
    herramientas_disponibles = Herramienta.objects.filter(
        activo=True, estado='disponible').count()
    herramientas_alquiladas = Herramienta.objects.filter(
        activo=True, estado='rentada').count()

    # Estadísticas de alquileres
    alquileres_activos = Alquiler.objects.filter(estado='activo').count()
    alquileres_vencidos = Alquiler.objects.filter(
        estado='activo', fecha_fin__lt=hoy).count()

    # Estadísticas de clientes
    total_clientes = Cliente.objects.count()

    # Ingresos del mes actual
    ingresos_mes = Alquiler.objects.filter(
        estado__in=['activo', 'devuelto'],
        fecha_creacion__month=hoy.month,
        fecha_creacion__year=hoy.year
    ).aggregate(total=Sum('total'))['total'] or 0

    # Total multas pendientes
    total_multas = Multa.objects.filter(
        estado='pendiente'
    ).aggregate(total=Sum('monto_total'))['total'] or 0

    # Últimos 5 alquileres registrados
    alquileres_recientes = Alquiler.objects.select_related(
        'cliente__usuario').order_by('-fecha_creacion')[:5]

    # Alquileres vencidos con días de retraso
    lista_vencidos = Alquiler.objects.filter(
        estado='activo',
        fecha_fin__lt=hoy
    ).select_related('cliente__usuario')[:5]

    context = {
        'total_herramientas': total_herramientas,
        'herramientas_disponibles': herramientas_disponibles,
        'herramientas_alquiladas': herramientas_alquiladas,
        'alquileres_activos': alquileres_activos,
        'alquileres_vencidos': alquileres_vencidos,
        'total_clientes': total_clientes,
        'ingresos_mes': ingresos_mes,
        'total_multas': total_multas,
        'alquileres_recientes': alquileres_recientes,
        'lista_vencidos': lista_vencidos,
    }

    return render(request, 'dashboard/index.html', context)