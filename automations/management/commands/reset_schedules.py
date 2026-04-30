from django.core.management.base import BaseCommand
from django.utils import timezone

from automations.models import AutomatedProcess, ScheduledTask, reset_scheduled_tasks_on_startup


class Command(BaseCommand):
    help = (
        "Reinicia las tareas programadas de Django Q a partir de los ScheduledTask "
        "activos y limpia cualquier lock de ejecución rancio en AutomatedProcess. "
        "Pensado para ser invocado UNA sola vez antes de levantar el qcluster."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-locks',
            action='store_true',
            default=False,
            help="No tocar el campo is_running de AutomatedProcess (no liberar locks).",
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE(
            f"[{timezone.now()}] Iniciando reset de tareas programadas..."
        ))

        if not options['skip_locks']:
            # Al arrancar el cluster, ningún proceso debería estar corriendo realmente.
            # Liberamos cualquier lock que haya quedado de una ejecución previa
            # interrumpida. Esto es crítico tras un reinicio inesperado del servidor.
            count = AutomatedProcess.objects.filter(is_running=True).update(
                is_running=False,
                running_started_at=None,
            )
            if count:
                self.stdout.write(self.style.WARNING(
                    f"  - Locks rancios liberados: {count}"
                ))
            else:
                self.stdout.write("  - No había locks rancios pendientes.")

        try:
            reset_scheduled_tasks_on_startup()
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"Error al reiniciar tareas programadas: {e}"
            ))
            return

        total = ScheduledTask.objects.filter(activo=True).count()
        self.stdout.write(self.style.SUCCESS(
            f"[{timezone.now()}] Reset completo. Tareas activas: {total}."
        ))
