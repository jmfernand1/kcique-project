from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'dexter'

# Crear un router y registrar los viewsets
router = DefaultRouter()

# Endpoints de datos
router.register(r'desembolsos', views.DesembolsoViewSet, basename='desembolso')
router.register(r'cargos-fijos', views.CargoFijoViewSet, basename='cargofijo')
router.register(r'garantias', views.GarantiaViewSet, basename='garantia')

# Endpoints de tracking ETL
router.register(r'ejecuciones', views.EjecucionETLViewSet, basename='ejecucion')
router.register(r'procesos-desembolso', views.ProcesoDesembolsoViewSet, basename='proceso-desembolso')
router.register(r'procesos-garantia', views.ProcesoGarantiaViewSet, basename='proceso-garantia')

# URLs de la aplicación web (frontend)
urlpatterns = [
    path('', views.dashboard_dexter, name='dashboard_dexter'),
    path('ejecuciones/', views.EjecucionETLListView.as_view(), name='ejecucion_list'),
    path('ejecuciones/<int:pk>/', views.EjecucionETLDetailView.as_view(), name='ejecucion_detail'),
]

# Añadir las URLs de la API
urlpatterns += [
    path('api/', include(router.urls)),
]
