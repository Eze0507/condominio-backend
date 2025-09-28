from rest_framework import serializers
from administracion.models import Persona
from ..models import contrato

class PersonaConSerializer(serializers.ModelSerializer):
    class Meta:
        model = Persona
        fields = ['id', 'nombre']

class ContratoSerializer(serializers.ModelSerializer):
    contrato_nombre=serializers.CharField(source='persona.nombre',read_only=True)
    class Meta:
        model = contrato
        fields = '__all__'