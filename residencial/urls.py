from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropietarioViewSet, InquilinoViewSet, FamiliaresViewSet,
    VisitanteViewSet
)
from .views_mascota import MascotaViewSet
from .views_visita import VisitaViewSet

# Router para gestión residencial
router = DefaultRouter()

# URLs para CRUD completo de cada tipo de persona
router.register(r'propietarios', PropietarioViewSet, basename='propietarios')
router.register(r'inquilinos', InquilinoViewSet, basename='inquilinos')
router.register(r'familiares', FamiliaresViewSet, basename='familiares')
router.register(r'visitantes', VisitanteViewSet, basename='visitantes')
router.register(r'mascotas', MascotaViewSet, basename='mascotas')
router.register(r'visitas', VisitaViewSet, basename='visitas')

urlpatterns = [
    path('', include(router.urls)),
]