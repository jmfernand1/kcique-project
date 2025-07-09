from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automations'
    
    def ready(self):
        """
        Método llamado cuando la aplicación está lista.
        Aquí reiniciamos las tareas programadas para evitar ejecuciones múltiples
        cuando se reinicia la aplicación.
        """
        try:
            from .models import reset_scheduled_tasks_on_startup
            reset_scheduled_tasks_on_startup()
        except Exception as e:
            print(f"Error al reiniciar tareas programadas: {e}")
            # No queremos que falle el arranque de la aplicación por esto
            pass
