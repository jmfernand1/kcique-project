from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .viewsets import (
    DesembolsoViewSet,
    CargoFijoViewSet,
    GarantiaViewSet,
    EjecucionETLViewSet,
    ProcesoDesembolsoViewSet,
    ProcesoGarantiaViewSet,
    EtapaProcesoDesembolsoViewSet,
    EtapaProcesoGarantiaViewSet,
    TipoDesembolsoViewSet,
    TipoGarantiaViewSet,
    EtapaTipoDesembolsoViewSet,
    EtapaTipoGarantiaViewSet
)
app_name = 'dexter'

# Crear un router y registrar los viewsets
router = DefaultRouter()

# Endpoints de datos
router.register(r'desembolsos', DesembolsoViewSet, basename='desembolso')
router.register(r'cargos-fijos', CargoFijoViewSet, basename='cargofijo')
router.register(r'garantias', GarantiaViewSet, basename='garantia')

# Endpoints de tracking ETL
router.register(r'ejecuciones', EjecucionETLViewSet, basename='ejecucion')
router.register(r'procesos-desembolso', ProcesoDesembolsoViewSet, basename='proceso-desembolso')
router.register(r'procesos-garantia', ProcesoGarantiaViewSet, basename='proceso-garantia')
router.register(r'etapas-proceso-desembolso', EtapaProcesoDesembolsoViewSet, basename='etapa-proceso-desembolso')
router.register(r'etapas-proceso-garantia', EtapaProcesoGarantiaViewSet, basename='etapa-proceso-garantia')
router.register(r'tipos-desembolso', TipoDesembolsoViewSet, basename='tipo-desembolso')
router.register(r'tipos-garantia', TipoGarantiaViewSet, basename='tipo-garantia')
router.register(r'etapas-desembolso', EtapaTipoDesembolsoViewSet, basename='etapa-desembolso')
router.register(r'etapas-garantia', EtapaTipoGarantiaViewSet, basename='etapa-garantia')

# URLs de la aplicación web (frontend)
urlpatterns = [
    path('', views.dashboard_dexter, name='dashboard_dexter'),
    path('ejecuciones/', views.EjecucionETLListView.as_view(), name='ejecucion_list'),
    path('ejecuciones/<int:pk>/', views.EjecucionETLDetailView.as_view(), name='ejecucion_detail'),
    
    # URLs para Desembolsos
    path('desembolsos/', views.DesembolsoListView.as_view(), name='desembolso_list'),
    path('desembolsos/crear/', views.DesembolsoCreateView.as_view(), name='desembolso_create'),
    path('desembolsos/<int:pk>/', views.DesembolsoDetailView.as_view(), name='desembolso_detail'),
    path('desembolsos/<int:pk>/editar/', views.DesembolsoUpdateView.as_view(), name='desembolso_update'),
    path('desembolsos/<int:pk>/eliminar/', views.DesembolsoDeleteView.as_view(), name='desembolso_delete'),
    
    # URLs para Garantías
    path('garantias/', views.GarantiaListView.as_view(), name='garantia_list'),
    path('garantias/crear/', views.GarantiaCreateView.as_view(), name='garantia_create'),
    path('garantias/<int:pk>/', views.GarantiaDetailView.as_view(), name='garantia_detail'),
    path('garantias/<int:pk>/editar/', views.GarantiaUpdateView.as_view(), name='garantia_update'),
    path('garantias/<int:pk>/eliminar/', views.GarantiaDeleteView.as_view(), name='garantia_delete'),
]

# Añadir las URLs de la API
urlpatterns += [
    path('api/', include(router.urls)),
]
