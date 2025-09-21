from rest_framework import serializers
from ..models import Propietario, Bloque, Unidad
from administracion.models import Persona
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


class PropietarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Propietario
    """
    persona = serializers.SerializerMethodField()
    nombre_completo = serializers.ReadOnlyField()
    telefono = serializers.ReadOnlyField()
    CI = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    tipo_propietario_display = serializers.CharField(source='get_tipo_propietario_display', read_only=True)
    estado_propietario_display = serializers.CharField(source='get_estado_propietario_display', read_only=True)
    
    class Meta:
        model = Propietario
        fields = [
            'persona', 'tipo_propietario', 'tipo_propietario_display',
            'fecha_registro_propietario', 'estado_propietario', 'estado_propietario_display',
            'porcentaje_propiedad', 'observaciones', 'email_alternativo',
            'telefono_alternativo', 'nombre_completo', 'telefono', 'CI', 'email'
        ]
        read_only_fields = ['fecha_registro_propietario']
    
    def get_persona(self, obj):
        """
        Obtener información de la persona asociada
        """
        if obj.persona:
            return {
                'id': obj.persona.id,
                'nombre': obj.persona.nombre,
                'apellido': obj.persona.apellido,
                'telefono': obj.persona.telefono,
                'foto': obj.persona.foto.url if obj.persona.foto else None,
                'estado': obj.persona.estado,
                'sexo': obj.persona.sexo,
                'CI': obj.persona.CI,
                'fecha_nacimiento': obj.persona.fecha_nacimiento,
                'fecha_registro': obj.persona.fecha_registro
            }
        return None
    
    
    def create(self, validated_data):
        """
        Crear propietario con persona asociada
        """
        # Obtener datos de persona del contexto
        persona_data = self.context.get('persona_data')
        if not persona_data:
            raise ValidationError("Se requiere información de persona para crear el propietario.")
        
        persona_data['tipo'] = 'R'  # Establecer como residente/propietario
        
        # Crear persona
        persona = Persona.objects.create(**persona_data)
        
        # Crear propietario
        propietario = Propietario.objects.create(persona=persona, **validated_data)
        return propietario
    
    def update(self, instance, validated_data):
        """
        Actualizar propietario
        """
        # Actualizar campos del propietario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class PropietarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear propietarios con datos de persona incluidos
    SIN CAMPO TIPO - Se asigna automáticamente como Propietario
    """
    # Campos de persona (SIN tipo)
    nombre = serializers.CharField(max_length=100, write_only=True)
    apellido = serializers.CharField(max_length=100, write_only=True)
    telefono = serializers.CharField(max_length=15, required=False, allow_blank=True, write_only=True)
    foto = serializers.ImageField(required=False, allow_null=True, write_only=True)
    sexo = serializers.ChoiceField(choices=Persona.SEXO_CHOICES, write_only=True)
    CI = serializers.CharField(max_length=20, write_only=True)
    fecha_nacimiento = serializers.DateField(write_only=True)
    
    # Campos de propietario
    estado_propietario_display = serializers.CharField(source='get_estado_propietario_display', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Propietario
        fields = [
            # Campos de persona
            'nombre', 'apellido', 'telefono', 'foto', 'sexo', 'CI', 'fecha_nacimiento',
            # Campos de propietario
            'estado_propietario', 'estado_propietario_display', 'observaciones', 'nombre_completo'
        ]
    
    def validate_CI(self, value):
        """
        Validar que la cédula sea única
        """
        if Persona.objects.filter(CI=value).exists():
            raise serializers.ValidationError("Esta cédula ya está registrada.")
        return value
    
    def validate_fecha_nacimiento(self, value):
        """
        Validar que la fecha de nacimiento no sea futura
        """
        if value > date.today():
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        return value
    
    def validate_porcentaje_propiedad(self, value):
        """
        Validar que el porcentaje de propiedad esté entre 0 y 100
        """
        if value < 0 or value > 100:
            raise serializers.ValidationError("El porcentaje de propiedad debe estar entre 0 y 100.")
        return value
    
    def create(self, validated_data):
        """
        Crear propietario con persona asociada
        """
        # Extraer datos de persona
        persona_data = {
            'nombre': validated_data.pop('nombre'),
            'apellido': validated_data.pop('apellido'),
            'telefono': validated_data.pop('telefono', ''),
            'foto': validated_data.pop('foto', None),
            'sexo': validated_data.pop('sexo'),
            'CI': validated_data.pop('CI'),
            'fecha_nacimiento': validated_data.pop('fecha_nacimiento'),
            'tipo': 'P',  # Establecer automáticamente como Propietario
            'estado': 'A'  # Activo por defecto
        }
        
        # Crear persona
        persona = Persona.objects.create(**persona_data)
        
        # Crear propietario
        propietario = Propietario.objects.create(persona=persona, **validated_data)
        return propietario


class PropietarioListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar propietarios
    """
    nombre_completo = serializers.ReadOnlyField()
    telefono = serializers.ReadOnlyField()
    CI = serializers.ReadOnlyField()
    estado_propietario_display = serializers.CharField(source='get_estado_propietario_display', read_only=True)
    
    class Meta:
        model = Propietario
        fields = [
            'persona', 'nombre_completo', 'estado_propietario', 'estado_propietario_display', 
            'fecha_registro_propietario', 'telefono', 'CI'
        ]


class BloqueSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Bloque
    """
    class Meta:
        model = Bloque
        fields = [
            'id', 'nombre', 'descripcion', 'numero_pisos', 'estado', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def validate_nombre(self, value):
        """
        Validar que el nombre del bloque sea único
        """
        if self.instance:
            if Bloque.objects.filter(nombre=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe un bloque con este nombre.")
        else:
            if Bloque.objects.filter(nombre=value).exists():
                raise serializers.ValidationError("Ya existe un bloque con este nombre.")
        return value


class UnidadSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Unidad
    """
    bloque_nombre = serializers.CharField(source='bloque.nombre', read_only=True)
    tipo_unidad_display = serializers.CharField(source='get_tipo_unidad_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    
    class Meta:
        model = Unidad
        fields = [
            'id', 'numero', 'codigo', 'descripcion', 'dimensiones', 'tipo_unidad',
            'tipo_unidad_display', 'estado', 'estado_display', 'bloque', 'bloque_nombre',
            'numero_piso', 'area_m2', 'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def validate_codigo(self, value):
        """
        Validar que el código de unidad sea único
        """
        if self.instance:
            if Unidad.objects.filter(codigo=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe una unidad con este código.")
        else:
            if Unidad.objects.filter(codigo=value).exists():
                raise serializers.ValidationError("Ya existe una unidad con este código.")
        return value
    
    def validate(self, data):
        """
        Validar que no exista una unidad duplicada en el mismo bloque
        """
        if self.instance:
            if Unidad.objects.filter(
                bloque=data.get('bloque', self.instance.bloque),
                numero=data.get('numero', self.instance.numero)
            ).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe una unidad con este número en el bloque especificado.")
        else:
            if Unidad.objects.filter(
                bloque=data['bloque'],
                numero=data['numero']
            ).exists():
                raise serializers.ValidationError("Ya existe una unidad con este número en el bloque especificado.")
        
        return data




class PropietarioStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de propietarios
    """
    total_propietarios = serializers.IntegerField()
    propietarios_activos = serializers.IntegerField()
    propietarios_inactivos = serializers.IntegerField()
    propietarios_con_contratos_activos = serializers.IntegerField()
