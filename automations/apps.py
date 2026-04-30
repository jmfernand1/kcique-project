from django.apps import AppConfig


class AutomationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'automations'

    def ready(self):
        """
        Antes este método llamaba a reset_scheduled_tasks_on_startup(), pero eso
        provocaba ejecuciones duplicadas porque ready() corre en CADA proceso
        Django (servidor web, master de qcluster y cada worker), generando
        Schedules duplicados o reseteando next_run varias veces casi en paralelo.

        Ahora la limpieza/reseteo se hace UNA sola vez vía el management command
        `python manage.py reset_schedules`, que se invoca desde iniciar_cluster.bat
        antes de levantar el qcluster.
        """
        return
