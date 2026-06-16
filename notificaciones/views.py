from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notificacion, PlantillaNotificacion
from .serializers import NotificacionSerializer, PlantillaNotificacionSerializer
from .services import enviar_whatsapp


@login_required
def lista(request):
    return render(request, 'notificaciones/lista.html')


# --- Plantillas ---

class PlantillaListView(generics.ListCreateAPIView):
    queryset = PlantillaNotificacion.objects.all()
    serializer_class = PlantillaNotificacionSerializer
    permission_classes = [IsAuthenticated]


class PlantillaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PlantillaNotificacion.objects.all()
    serializer_class = PlantillaNotificacionSerializer
    permission_classes = [IsAuthenticated]


# --- Notificaciones ---

class NotificacionListView(generics.ListAPIView):
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notificacion.objects.all()
        cliente_id = self.request.query_params.get('cliente')
        estado = self.request.query_params.get('estado')
        canal = self.request.query_params.get('canal')

        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if canal:
            queryset = queryset.filter(canal=canal)

        return queryset


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_notificacion_manual(request):
    """
    Envía una notificación manual a un cliente.
    Body: { cliente_id, tipo_plantilla, contexto }
    """
    cliente_id = request.data.get('cliente_id')
    tipo_plantilla = request.data.get('tipo_plantilla')
    contexto = request.data.get('contexto', {})

    if not cliente_id or not tipo_plantilla:
        return Response(
            {'error': 'cliente_id y tipo_plantilla son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from clientes.models import Cliente
        cliente = Cliente.objects.get(id=cliente_id)
    except Cliente.DoesNotExist:
        return Response(
            {'error': 'Cliente no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    exito, mensaje = enviar_whatsapp(cliente, tipo_plantilla, contexto)

    if exito:
        return Response({'mensaje': mensaje}, status=status.HTTP_200_OK)
    else:
        return Response({'error': mensaje}, status=status.HTTP_400_BAD_REQUEST)