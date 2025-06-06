from django.urls import path
from . import views

app_name = 'adagio' # Es una buena práctica definir el namespace de la app

urlpatterns = [
    path('', views.dashboard_adagio, name='dashboard_adagio'),
    # Podríamos añadir una URL específica para la carga si quisiéramos separar la lógica,
    # pero por ahora la manejaremos en la misma vista del dashboard.
] 