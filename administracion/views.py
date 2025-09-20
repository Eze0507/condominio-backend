from rest_framework import status, viewsets
from django.contrib.auth.models import User, Group
from .serializers.serializersUser import UserSerializer, GroupAuxSerializer
from .serializers.serializersRol import RolSerializer, RolListSerializer
from django.db.models import ProtectedError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

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

class RolViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RolListSerializer  
        return RolSerializer          

