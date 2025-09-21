from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropietarioViewSet, BloqueViewSet, UnidadViewSet
)

# Router para CU9: Gestionar Propietarios
router = DefaultRouter()

# URLs para CU9: Gestionar Propietarios
router.register(r'propietarios', PropietarioViewSet, basename='propietarios')
router.register(r'bloques', BloqueViewSet, basename='bloques')
router.register(r'unidades', UnidadViewSet, basename='unidades')

urlpatterns = [
    path('', include(router.urls)),
]