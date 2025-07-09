from django.urls import path
from . import views

app_name = 'automations'

urlpatterns = [
    path('', views.ProcessListView.as_view(), name='process_list'),
    path('process/<int:pk>/', views.ProcessDetailView.as_view(), name='process_detail'),
    path('process/new/', views.ProcessCreateView.as_view(), name='process_create'),
    path('process/<int:pk>/update/', views.ProcessUpdateView.as_view(), name='process_update'),
    path('process/<int:pk>/delete/', views.ProcessDeleteView.as_view(), name='process_delete'),
    path('process/<int:process_id>/run/', views.run_process_view, name='run_process'),
    path('log/<int:log_id>/output/', views.get_log_output, name='get_log_output'), # Para polling de logs

    # URLs para Tareas Programadas
    path('scheduled-tasks/', views.ScheduledTaskListView.as_view(), name='scheduledtask_list'),
    path('scheduled-tasks/new/', views.ScheduledTaskCreateView.as_view(), name='scheduledtask_create'),
    # Crear tarea para un proceso específico
    path('process/<int:process_pk>/schedule/', views.ScheduledTaskCreateView.as_view(), name='scheduledtask_create_for_process'),
    path('scheduled-tasks/<int:pk>/update/', views.ScheduledTaskUpdateView.as_view(), name='scheduledtask_update'),
    path('scheduled-tasks/<int:pk>/delete/', views.ScheduledTaskDeleteView.as_view(), name='scheduledtask_delete'),

    # URL para el estado del clúster
    path('cluster-status/', views.cluster_status_view, name='cluster_status'),
] 