from rest_framework import serializers
from ..models import vehiculo
from administracion.models import Persona  


class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = vehiculo
        fields = '__all__'
        read_only_fields = ['fecha_registro']

class PersonaAuxSerializers(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'nombre']
