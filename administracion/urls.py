from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.views import (
    tokenObtainPairView,
    tokenRefreshView,
)

urlpatterns = [
    path('login/', tokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', tokenRefreshView.as_view(), name='token_refresh'),
]