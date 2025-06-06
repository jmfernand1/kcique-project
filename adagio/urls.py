from django.urls import path
from . import views

app_name = 'adagio' # Es una buena práctica definir el namespace de la app

urlpatterns = [
    path('', views.dashboard_adagio, name='dashboard_adagio'),
    # Podríamos añadir una URL específica para la carga si quisiéramos separar la lógica,
    # pero por ahora la manejaremos en la misma vista del dashboard.
    path('casos/', views.CasoDebitoListView.as_view(), name='casopendiente_list'),
    path('casos/nuevo/', views.CasoDebitoCreateView.as_view(), name='casopendiente_create'),
    path('casos/<int:pk>/', views.CasoDebitoDetailView.as_view(), name='casopendiente_detail'),
    path('casos/<int:pk>/editar/', views.CasoDebitoUpdateView.as_view(), name='casopendiente_update'),
    path('casos/<int:pk>/eliminar/', views.CasoDebitoDeleteView.as_view(), name='casopendiente_delete'),
] 