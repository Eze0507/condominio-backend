from rest_framework import status, viewsets, filters
from django.db.models import Q, Count, Avg
from django.db.models import ProtectedError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from .serializers.serializersPropietario import (
    PropietarioSerializer, PropietarioCreateSerializer, PropietarioListSerializer,
    BloqueSerializer, UnidadSerializer, PropietarioStatsSerializer
)
from .models import Propietario, Bloque, Unidad
from administracion.models import Persona

# Create your views here.

# ==================== VISTAS PARA CU9: GESTIONAR PROPIETARIOS ====================

class PropietarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar propietarios
    SIN AUTENTICACIÓN - Acceso libre
    """
    queryset = Propietario.objects.select_related('persona').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'persona__nombre', 'persona__apellido', 'persona__CI', 
        'email_alternativo', 'telefono_alternativo'
    ]
    ordering_fields = [
        'persona__apellido', 'persona__nombre', 'fecha_registro_propietario',
        'tipo_propietario', 'estado_propietario', 'porcentaje_propiedad'
    ]
    ordering = ['persona__apellido', 'persona__nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropietarioListSerializer
        elif self.action == 'create':
            return PropietarioCreateSerializer
        return PropietarioSerializer
    
    def get_queryset(self):
        """
        Filtrar propietarios por diferentes criterios
        """
        queryset = super().get_queryset()
        
        # Filtrar por tipo de propietario
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo_propietario=tipo)
        
        # Filtrar por estado del propietario
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado_propietario=estado)
        
        # Filtrar por rango de porcentaje de propiedad
        porcentaje_min = self.request.query_params.get('porcentaje_min', None)
        porcentaje_max = self.request.query_params.get('porcentaje_max', None)
        if porcentaje_min:
            queryset = queryset.filter(porcentaje_propiedad__gte=porcentaje_min)
        if porcentaje_max:
            queryset = queryset.filter(porcentaje_propiedad__lte=porcentaje_max)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadísticas de propietarios
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_propietarios': queryset.count(),
            'propietarios_activos': queryset.filter(estado_propietario='A').count(),
            'propietarios_inactivos': queryset.filter(estado_propietario='I').count(),
            'total_copropietarios': queryset.filter(tipo_propietario='C').count(),
            'total_arrendatarios': queryset.filter(tipo_propietario='A').count(),
            'promedio_porcentaje_propiedad': queryset.aggregate(promedio=Avg('porcentaje_propiedad'))['promedio'] or 0,
            'propietarios_con_contratos_activos': queryset.filter(
                contrato__estado='A'
            ).distinct().count(),
        }
        
        serializer = PropietarioStatsSerializer(stats)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activar un propietario
        """
        propietario = self.get_object()
        propietario.estado_propietario = 'A'
        propietario.save()
        return Response({'message': 'Propietario activado correctamente'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactivar un propietario
        """
        propietario = self.get_object()
        propietario.estado_propietario = 'I'
        propietario.save()
        return Response({'message': 'Propietario desactivado correctamente'})


class BloqueViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar bloques
    SIN AUTENTICACIÓN - Acceso libre
    """
    queryset = Bloque.objects.all()
    serializer_class = BloqueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'numero_pisos', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_queryset(self):
        """
        Filtrar bloques por estado activo si se especifica
        """
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado', None)
        if estado is not None:
            queryset = queryset.filter(estado=estado.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['get'])
    def unidades(self, request, pk=None):
        """
        Obtener unidades de un bloque específico
        """
        bloque = self.get_object()
        unidades = Unidad.objects.filter(bloque=bloque).order_by('numero_piso', 'numero')
        serializer = UnidadSerializer(unidades, many=True)
        return Response(serializer.data)


class UnidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar unidades
    SIN AUTENTICACIÓN - Acceso libre
    """
    queryset = Unidad.objects.select_related('bloque').all()
    serializer_class = UnidadSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero', 'codigo', 'descripcion', 'bloque__nombre']
    ordering_fields = ['numero', 'codigo', 'numero_piso', 'area_m2', 'fecha_creacion']
    ordering = ['bloque__nombre', 'numero_piso', 'numero']
    
    def get_queryset(self):
        """
        Filtrar unidades por diferentes criterios
        """
        queryset = super().get_queryset()
        
        # Filtrar por bloque
        bloque = self.request.query_params.get('bloque', None)
        if bloque:
            queryset = queryset.filter(bloque_id=bloque)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por tipo de unidad
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo_unidad=tipo)
        
        # Filtrar por piso
        piso = self.request.query_params.get('piso', None)
        if piso:
            queryset = queryset.filter(numero_piso=piso)
        
        return queryset
    


