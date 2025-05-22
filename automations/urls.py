from django.urls import path
from . import views

app_name = 'automations'

urlpatterns = [
    path('', views.process_list, name='process_list'),
    path('process/<int:pk>/', views.process_detail, name='process_detail'),
    path('process/create/', views.process_create, name='process_create'),
    path('process/<int:pk>/update/', views.process_update, name='process_update'),
    path('process/<int:pk>/delete/', views.process_delete, name='process_delete'),
    path('process/<int:process_id>/run/', views.run_process_view, name='run_process'),
    path('log/<int:log_id>/output/', views.get_log_output, name='get_log_output'), # Para polling de logs
] 