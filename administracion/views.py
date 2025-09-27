from rest_framework import status, viewsets, filters, generics
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
from .serializers.serializersPersona import PersonaSerializer
from .serializers.serializersEmpleado import CargoSerializer, EmpleadoSerializer, EmpleadoListSerializer
from .models import Persona, Cargo, Empleado
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
import requests
from django.conf import settings

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


# ==================== VISTAS PARA GESTIONAR PERSONAS ====================

class PersonaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar personas con subida de imágenes a ImgBB
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
    
    def create(self, request, *args, **kwargs):
        """
        Crear persona con subida de imagen a ImgBB
        """
        return self.handle_image_upload(request, super().create, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar persona con subida de imagen a ImgBB
        """
        return self.handle_image_upload(request, super().update, *args, **kwargs)
    
    def handle_image_upload(self, request, action, *args, **kwargs):
        """
        Maneja la subida de imágenes a ImgBB API
        """
        imagen_file = request.FILES.get('imagen')
        
        if imagen_file:
            # Subir imagen a ImgBB
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": settings.IMGBB_API_KEY}
            files = {"image": imagen_file.read()}
            
            response = requests.post(url, payload, files=files)
            
            if response.status_code == 200:
                # Extraer URL de la imagen subida
                image_url = response.json()["data"]["url"]
                
                # Actualizar los datos de la request con la URL de la imagen
                data = request.data.copy()
                data["imagen"] = image_url
                request._full_data = data
            else:
                return Response(
                    {"error": "Error al subir imagen a ImgBB"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Si no se sube nueva imagen en PUT/PATCH, mantener la existente
            if request.method in ["PUT", "PATCH"]:
                instance = self.get_object()
                data = request.data.copy()
                if not data.get("imagen"):
                    data["imagen"] = instance.imagen
                request._full_data = data
        
        return action(request, *args, **kwargs)


# ==================== VISTAS PARA GESTIONAR EMPLEADOS ====================

class CargoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cargos
    """
    queryset = Cargo.objects.all()
    serializer_class = CargoSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre']
    ordering_fields = ['nombre']
    ordering = ['nombre']


class EmpleadoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar empleados con subida de imágenes a ImgBB
    """
    queryset = Empleado.objects.select_related('cargo').all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        'nombre', 'apellido', 'CI', 'cargo__nombre'
    ]
    ordering_fields = [
        'apellido', 'nombre', 'sueldo', 'estado'
    ]
    ordering = ['apellido', 'nombre']
    
    def get_serializer_class(self):
        if self.action == 'list':
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
            queryset = queryset.filter(estado=estado)
        
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
    
    def create(self, request, *args, **kwargs):
        """
        Crear empleado con subida de imagen a ImgBB
        """
        return self.handle_image_upload(request, super().create, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        """
        Actualizar empleado con subida de imagen a ImgBB
        """
        return self.handle_image_upload(request, super().update, *args, **kwargs)
    
    def handle_image_upload(self, request, action, *args, **kwargs):
        """
        Maneja la subida de imágenes a ImgBB API
        """
        imagen_file = request.FILES.get('imagen')
        
        if imagen_file:
            # Subir imagen a ImgBB
            url = "https://api.imgbb.com/1/upload"
            payload = {"key": settings.IMGBB_API_KEY}
            files = {"image": imagen_file.read()}
            
            response = requests.post(url, payload, files=files)
            
            if response.status_code == 200:
                # Extraer URL de la imagen subida
                image_url = response.json()["data"]["url"]
                
                # Actualizar los datos de la request con la URL de la imagen
                data = request.data.copy()
                data["imagen"] = image_url
                request._full_data = data
            else:
                return Response(
                    {"error": "Error al subir imagen a ImgBB"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            # Si no se sube nueva imagen en PUT/PATCH, mantener la existente
            if request.method in ["PUT", "PATCH"]:
                instance = self.get_object()
                data = request.data.copy()
                if not data.get("imagen"):
                    data["imagen"] = instance.imagen
                request._full_data = data
        
        return action(request, *args, **kwargs)




@method_decorator(csrf_exempt, name='dispatch')
class CustomTokenObtainPairView(TokenObtainPairView):
    authentication_classes = []
    permission_classes = [AllowAny]

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({ "detail": "CSRF cookie set" })