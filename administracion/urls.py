from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LogoutView, UserViewSet, RolViewSet,
    PersonaViewSet, CargoViewSet, EmpleadoViewSet
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Router principal
router = DefaultRouter()

# URLs existentes (CU1, CU2, CU3, CU4, CU5)
router.register(r'users', UserViewSet, basename='users')
router.register(r'roles', RolViewSet, basename='roles')

# URLs para CU6: Gestionar Empleado
router.register(r'personas', PersonaViewSet, basename='personas')
router.register(r'cargos', CargoViewSet, basename='cargos')
router.register(r'empleados', EmpleadoViewSet, basename='empleados')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]