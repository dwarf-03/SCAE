from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SesionChat, MensajeChat
from inventario.models import Herramienta, Categoria
from alquileres.models import Alquiler
from clientes.models import Cliente
from multas.models import Multa
from django.utils import timezone
from django.db.models import Sum
import json
import requests

def obtener_contexto_sistema():
    # Obtiene datos reales de la BD para el contexto del chatbot
    herramientas_disponibles = Herramienta.objects.filter(
        activo=True, estado='disponible'
    ).select_related('categoria')

    alquileres_activos = Alquiler.objects.filter(estado='activo').count()
    total_clientes = Cliente.objects.count()
    multas_pendientes = Multa.objects.filter(estado='pendiente').aggregate(
        total=Sum('monto_total'))['total'] or 0

    # Construye lista de herramientas disponibles
    lista_herramientas = []
    for h in herramientas_disponibles:
        lista_herramientas.append(
            f"- {h.nombre} (Código: {h.codigo}, Categoría: {h.categoria.nombre}, "
            f"Precio: ${h.precio_diario}/día, Disponibles: {h.cantidad_disponible})"
        )

    herramientas_str = '\n'.join(lista_herramientas) if lista_herramientas else 'No hay herramientas disponibles'

    return f"""
Eres el asistente virtual de SCAE (Sistema de Control y Alquiler de Equipos de Construcción).
Eres amable, profesional y respondes en español.

INFORMACIÓN ACTUAL DEL SISTEMA:
- Alquileres activos: {alquileres_activos}
- Total de clientes: {total_clientes}
- Multas pendientes: ${multas_pendientes:,.0f}

HERRAMIENTAS DISPONIBLES AHORA:
{herramientas_str}

PUEDES AYUDAR CON:
- Consultar disponibilidad de herramientas
- Informar precios y costos de alquiler
- Explicar el proceso de alquiler
- Informar sobre multas y devoluciones
- Dar información de contacto y horarios
- Responder preguntas sobre el sistema

INFORMACIÓN DE CONTACTO:
- Horario: Lunes a Sábado 8am - 6pm
- Para alquilar: Visítanos o contacta a un asesor

IMPORTANTE:
- Sé conciso y claro en tus respuestas
- Si no tienes información específica, indica que un asesor puede ayudar
- No inventes precios ni disponibilidades que no estén en el sistema
"""


@login_required
def index(request):
    # Obtiene o crea sesión de chat para el usuario
    sesion, created = SesionChat.objects.get_or_create(
        usuario=request.user,
        canal='web',
        activa=True,
        defaults={'contexto': {}}
    )

    # Obtiene historial de mensajes
    mensajes = sesion.mensajes.order_by('fecha_envio')

    return render(request, 'chatbot/index.html', {
        'sesion': sesion,
        'mensajes': mensajes,
    })


@login_required
def enviar_mensaje(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        mensaje_usuario = data.get('mensaje', '').strip()

        if not mensaje_usuario:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

        # Obtiene o crea sesión activa
        sesion, created = SesionChat.objects.get_or_create(
            usuario=request.user,
            canal='web',
            activa=True,
            defaults={'contexto': {}}
        )

        # Guarda mensaje del usuario
        MensajeChat.objects.create(
            sesion=sesion,
            tipo='usuario',
            contenido=mensaje_usuario,
        )

        # Obtiene historial para contexto
        historial = sesion.mensajes.order_by('fecha_envio')
        messages_history = []
        for msg in historial:
            role = 'user' if msg.tipo == 'usuario' else 'assistant'
            messages_history.append({
                'role': role,
                'content': msg.contenido
            })

        import requests

        # Llama a Ollama local
        response = requests.post(
            'http://localhost:11434/api/chat',
            json={
                'model': 'llama3.2:1b',
                'messages': [
                    {'role': 'system', 'content': obtener_contexto_sistema()},
                    *messages_history
                ],
                'stream': False,
            }
        )

        data = response.json()
        respuesta_bot = data['message']['content']

        # Guarda respuesta del bot
        MensajeChat.objects.create(
            sesion=sesion,
            tipo='bot',
            contenido=respuesta_bot,
        )

        return JsonResponse({
            'respuesta': respuesta_bot,
            'timestamp': timezone.now().strftime('%H:%M'),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def limpiar_chat(request):
    if request.method == 'POST':
        # Desactiva la sesión actual
        SesionChat.objects.filter(
            usuario=request.user,
            canal='web',
            activa=True
        ).update(activa=False)

        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Método no permitido'}, status=405)