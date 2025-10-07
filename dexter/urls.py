from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dexter'

# Crear un router y registrar los viewsets
router = DefaultRouter()
router.register(r'desembolsos', views.DesembolsoViewSet, basename='desembolso')
router.register(r'cargos-fijos', views.CargoFijoViewSet, basename='cargofijo')
router.register(r'garantias', views.GarantiaViewSet, basename='garantia')

# Las URLs de la API
urlpatterns = [
    path('api/', include(router.urls)),
]

