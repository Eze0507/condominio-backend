from rest_framework import status, viewsets, filters
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Q, Count, Avg, Sum
from django.db.models import ProtectedError
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from .serializers.serializersUser import UserSerializer, GroupAuxSerializer
from .serializers.serializersRol import RolSerializer, RolListSerializer, PermissionSerializer
from .serializers.serializersEmpleado import (
    PersonaSerializer, CargoSerializer, EmpleadoSerializer, EmpleadoCreateSerializer,
    EmpleadoListSerializer, EmpleadoStatsSerializer
)
from .models import Persona, Cargo, Empleado
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView

# Create your views here.
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist() 
            return Response({"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ProtectedError:
            return Response(
                {"detail": "No se puede eliminar este usuario porque está asociado a otros registros"},
                status=status.HTTP_400_BAD_REQUEST
            )

class GroupAuxViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupAuxSerializer

class PermissionViewSet(viewsets.ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer

class RolViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RolListSerializer  
        return RolSerializer          


# ==================== VISTAS PARA CU6: GESTIONAR EMPLEADO ====================

class PersonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar personas
    """
    queryset = Persona.objects.all()
    serializer_class = PersonaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'apellido', 'CI', 'telefono']
    ordering_fields = ['nombre', 'apellido', 'fecha_registro', 'CI']
    ordering = ['apellido', 'nombre']
    
    def get_queryset(self):
        """
        Filtrar por tipo de persona si se especifica
        """
        queryset = super().get_queryset()
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        return queryset


class CargoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cargos
    """
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'salario_base', 'fecha_creacion']
    ordering = ['nombre']
    
    def get_queryset(self):
        """
        Filtrar por estado activo si se especifica
        """
        queryset = super().get_queryset()
        estado = self.request.query_params.get('estado', None)
        if estado is not None:
            queryset = queryset.filter(estado=estado.lower() == 'true')
        return queryset


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empleados
    """
    queryset = Empleado.objects.select_related('persona', 'cargo').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'persona__nombre', 'persona__apellido', 'persona__CI', 
        'numero_empleado', 'cargo__nombre'
    ]
    ordering_fields = [
        'persona__apellido', 'persona__nombre', 'fecha_ingreso', 
        'sueldo', 'estado_empleado'
    ]
    ordering = ['persona__apellido', 'persona__nombre']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return EmpleadoCreateSerializer
        elif self.action == 'list':
            return EmpleadoListSerializer
        return EmpleadoSerializer
    
    def get_queryset(self):
        """
        Filtrar empleados por diferentes criterios
        """
        queryset = super().get_queryset()
        
        # Filtrar por estado del empleado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado_empleado=estado)
        
        # Filtrar por cargo
        cargo = self.request.query_params.get('cargo', None)
        if cargo:
            queryset = queryset.filter(cargo_id=cargo)
        
        # Filtrar por rango de sueldo
        sueldo_min = self.request.query_params.get('sueldo_min', None)
        sueldo_max = self.request.query_params.get('sueldo_max', None)
        if sueldo_min:
            queryset = queryset.filter(sueldo__gte=sueldo_min)
        if sueldo_max:
            queryset = queryset.filter(sueldo__lte=sueldo_max)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadísticas de empleados
        """
        queryset = self.get_queryset()
        
        stats = {
            'total_empleados': queryset.count(),
            'empleados_activos': queryset.filter(estado_empleado='A').count(),
            'empleados_inactivos': queryset.filter(estado_empleado='I').count(),
            'total_sueldos': queryset.aggregate(total=Sum('sueldo'))['total'] or 0,
            'promedio_sueldo': queryset.aggregate(promedio=Avg('sueldo'))['promedio'] or 0,
        }
        
        # Cargo más común
        cargo_mas_comun = queryset.values('cargo__nombre').annotate(
            count=Count('cargo')
        ).order_by('-count').first()
        
        stats['cargo_mas_comun'] = cargo_mas_comun['cargo__nombre'] if cargo_mas_comun else 'N/A'
        
        serializer = EmpleadoStatsSerializer(stats)
        return Response(serializer.data)
    
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Activar un empleado
        """
        empleado = self.get_object()
        empleado.estado_empleado = 'A'
        empleado.save()
        return Response({'message': 'Empleado activado correctamente'})
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Desactivar un empleado
        """
        empleado = self.get_object()
        empleado.estado_empleado = 'I'
        empleado.save()
        return Response({'message': 'Empleado desactivado correctamente'})

@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({ "detail": "CSRF cookie set" })



