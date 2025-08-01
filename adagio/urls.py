from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'adagio' # Es una buena práctica definir el namespace de la app

# Crear un router y registrar nuestro viewset
router = DefaultRouter()
router.register(r'casos', views.CasoDebitoViewSet, basename='casodebito')

# Las URLs de la aplicación web
urlpatterns = [
    path('', views.dashboard_adagio, name='dashboard_adagio'),
    # Podríamos añadir una URL específica para la carga si quisiéramos separar la lógica,
    # pero por ahora la manejaremos en la misma vista del dashboard.
    path('casos/', views.CasoDebitoListView.as_view(), name='casopendiente_list'),
    path('casos/nuevo/', views.CasoDebitoCreateView.as_view(), name='casopendiente_create'),
    path('casos/<int:pk>/', views.CasoDebitoDetailView.as_view(), name='casopendiente_detail'),
    path('casos/<int:pk>/editar/', views.CasoDebitoUpdateView.as_view(), name='casopendiente_update'),
    path('casos/<int:pk>/eliminar/', views.CasoDebitoDeleteView.as_view(), name='casopendiente_delete'),
    
    # URLs de descarga CSV
    path('descargar/todos/', views.descargar_todos_casos, name='descargar_todos_casos'),
    path('descargar/pendientes/', views.descargar_casos_pendientes, name='descargar_casos_pendientes'),
    path('descargar/pendiente-bizagi/', views.descargar_casos_pendiente_bizagi, name='descargar_casos_pendiente_bizagi'),
    path('descargar/grabado/', views.descargar_casos_grabado, name='descargar_casos_grabado'),
    path('descargar/finalizado/', views.descargar_casos_finalizado, name='descargar_casos_finalizado'),
    path('descargar/con-error/', views.descargar_casos_con_error, name='descargar_casos_con_error'),
    path('descargar/validar/', views.descargar_casos_validar, name='descargar_casos_validar'),
]

# Añadir las URLs de la API
urlpatterns += [
    path('api/', include(router.urls)),
] 