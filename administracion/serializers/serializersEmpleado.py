from rest_framework import serializers
from ..models import Persona, Cargo, Empleado
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date


class PersonaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Persona
    """
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Persona
        fields = [
            'id', 'nombre', 'apellido', 'telefono', 'foto', 'estado', 
            'sexo', 'tipo', 'fecha_registro', 'CI', 'fecha_nacimiento', 
            'nombre_completo'
        ]
        read_only_fields = ['id', 'fecha_registro']
    
    def validate_CI(self, value):
        """
        Validar que la cédula sea única
        """
        if self.instance:
            if Persona.objects.filter(CI=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Esta cédula ya está registrada.")
        else:
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


class CargoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Cargo
    """
    class Meta:
        model = Cargo
        fields = [
            'id', 'nombre', 'descripcion', 'salario_base', 'estado', 
            'fecha_creacion'
        ]
        read_only_fields = ['id', 'fecha_creacion']
    
    def validate_nombre(self, value):
        """
        Validar que el nombre del cargo sea único
        """
        if self.instance:
            if Cargo.objects.filter(nombre=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Ya existe un cargo con este nombre.")
        else:
            if Cargo.objects.filter(nombre=value).exists():
                raise serializers.ValidationError("Ya existe un cargo con este nombre.")
        return value


class PersonaEmpleadoSerializer(serializers.ModelSerializer):
    """
    Serializer para Persona específico para empleados (sin campo tipo)
    """
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Persona
        fields = [
            'id', 'nombre', 'apellido', 'telefono', 'foto', 'estado', 
            'sexo', 'fecha_registro', 'CI', 'fecha_nacimiento', 
            'nombre_completo'
        ]
        read_only_fields = ['id', 'fecha_registro', 'tipo']
    
    def validate_CI(self, value):
        """
        Validar que la cédula sea única
        """
        if self.instance:
            if Persona.objects.filter(CI=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Esta cédula ya está registrada.")
        else:
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


class EmpleadoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Empleado
    """
    persona = PersonaSerializer()
    cargo_nombre = serializers.CharField(source='cargo.nombre', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Empleado
        fields = [
            'persona', 'direccion', 'sueldo', 'fecha_ingreso', 'fecha_salida',
            'estado_empleado', 'cargo', 'cargo_nombre', 'numero_empleado',
            'nombre_completo'
        ]
        read_only_fields = ['numero_empleado']


class EmpleadoCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear empleados (sin campos tipo y fecha_ingreso)
    """
    persona = PersonaEmpleadoSerializer()
    cargo_nombre = serializers.CharField(source='cargo.nombre', read_only=True)
    nombre_completo = serializers.ReadOnlyField()
    
    class Meta:
        model = Empleado
        fields = [
            'persona', 'direccion', 'sueldo', 'fecha_salida',
            'estado_empleado', 'cargo', 'cargo_nombre', 'numero_empleado',
            'nombre_completo'
        ]
        read_only_fields = ['numero_empleado']
    
    
    def validate_numero_empleado(self, value):
        """
        Validar que el número de empleado sea único
        """
        if self.instance:
            if Empleado.objects.filter(numero_empleado=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Este número de empleado ya está en uso.")
        else:
            if Empleado.objects.filter(numero_empleado=value).exists():
                raise serializers.ValidationError("Este número de empleado ya está en uso.")
        return value
    
    def validate_fecha_ingreso(self, value):
        """
        Validar que la fecha de ingreso no sea futura
        """
        if value > date.today():
            raise serializers.ValidationError("La fecha de ingreso no puede ser futura.")
        return value
    
    def validate_fecha_salida(self, value):
        """
        Validar que la fecha de salida sea posterior a la fecha de ingreso
        """
        if value and 'fecha_ingreso' in self.initial_data:
            fecha_ingreso = self.initial_data['fecha_ingreso']
            if isinstance(fecha_ingreso, str):
                from datetime import datetime
                fecha_ingreso = datetime.strptime(fecha_ingreso, '%Y-%m-%d').date()
            if value <= fecha_ingreso:
                raise serializers.ValidationError("La fecha de salida debe ser posterior a la fecha de ingreso.")
        return value
    
    def validate_sueldo(self, value):
        """
        Validar que el sueldo sea positivo
        """
        if value <= 0:
            raise serializers.ValidationError("El sueldo debe ser mayor a 0.")
        return value
    
    def create(self, validated_data):
        """
        Crear empleado con persona asociada
        """
        persona_data = validated_data.pop('persona')
        persona_data['tipo'] = 'E'  # Establecer automáticamente como empleado
        persona_data['estado'] = 'A'  # Activo por defecto
        
        # Crear persona
        persona = Persona.objects.create(**persona_data)
        
        # Generar número de empleado automático
        if not validated_data.get('numero_empleado'):
            ultimo_empleado = Empleado.objects.order_by('-numero_empleado').first()
            if ultimo_empleado:
                try:
                    siguiente_numero = int(ultimo_empleado.numero_empleado) + 1
                except ValueError:
                    siguiente_numero = 1
            else:
                siguiente_numero = 1
            validated_data['numero_empleado'] = f"EMP{siguiente_numero:04d}"
        
        # Establecer fecha de ingreso automáticamente
        validated_data['fecha_ingreso'] = timezone.now().date()
        
        # Crear empleado
        empleado = Empleado.objects.create(persona=persona, **validated_data)
        return empleado
    
    def update(self, instance, validated_data):
        """
        Actualizar empleado y persona asociada
        """
        persona_data = validated_data.pop('persona', None)
        
        if persona_data:
            persona_serializer = PersonaSerializer(instance.persona, data=persona_data, partial=True)
            if persona_serializer.is_valid():
                persona_serializer.save()
            else:
                raise ValidationError(persona_serializer.errors)
        
        # Actualizar campos del empleado
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class EmpleadoListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listar empleados
    """
    nombre_completo = serializers.ReadOnlyField()
    cargo_nombre = serializers.CharField(source='cargo.nombre', read_only=True)
    telefono = serializers.ReadOnlyField()
    CI = serializers.ReadOnlyField()
    
    class Meta:
        model = Empleado
        fields = [
            'persona', 'nombre_completo', 'cargo_nombre', 'sueldo',
            'fecha_ingreso', 'estado_empleado', 'numero_empleado',
            'telefono', 'CI'
        ]




class EmpleadoStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de empleados
    """
    total_empleados = serializers.IntegerField()
    empleados_activos = serializers.IntegerField()
    empleados_inactivos = serializers.IntegerField()
    total_sueldos = serializers.DecimalField(max_digits=12, decimal_places=2)
    cargo_mas_comun = serializers.CharField()
    promedio_sueldo = serializers.DecimalField(max_digits=10, decimal_places=2)
