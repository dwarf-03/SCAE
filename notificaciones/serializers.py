from rest_framework import serializers
from .models import Notificacion, PlantillaNotificacion


class PlantillaNotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaNotificacion
        fields = '__all__'


class NotificacionSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='cliente.nombre_completo', read_only=True)
    plantilla_tipo = serializers.CharField(source='plantilla.get_tipo_display', read_only=True)

    class Meta:
        model = Notificacion
        fields = '__all__'