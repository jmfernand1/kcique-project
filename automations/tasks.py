from django.utils import timezone

from .models import AutomatedProcess, ScheduledTask
from .process_executor import run_process_safely, is_process_running


def execute_automated_process(*args, **kwargs):
    """
    Tarea de Django-Q que busca un AutomatedProcess por su ID y lo ejecuta de forma
    SINCRÓNICA dentro del worker. Acepta kwargs para ser compatible con la forma en
    que django-q invoca las tareas.

    - Verifica el rango de horas (hora_inicio/hora_fin) si está configurado.
    - El chequeo de "ya está en ejecución" final se hace dentro de run_process_safely
      con un select_for_update atómico, válido entre todos los workers.
    - Como la ejecución es sincrónica, el worker permanece ocupado durante todo el
      tiempo que dura el script. Esto evita que Django Q vuelva a entregar la misma
      tarea al mismo worker mientras corre.
    """
    task_id = kwargs.get('task_id')
    if task_id is None:
        if args:
            task_id = args[0]
        else:
            error_msg = "Error: No se pudo ejecutar la tarea programada. No se proporcionó 'task_id'."
            print(error_msg)
            return error_msg

    try:
        process = AutomatedProcess.objects.get(id=task_id)
    except AutomatedProcess.DoesNotExist:
        error_msg = f"Error: Proceso con ID {task_id} no encontrado."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error inesperado al consultar el proceso ID {task_id}: {e}"
        print(error_msg)
        return error_msg

    if not process.is_active:
        skip_msg = f"[{timezone.now()}] Omitiendo '{process.name}' - el proceso está inactivo."
        print(skip_msg)
        return skip_msg

    # Pre-chequeo barato (no atómico). Evita trabajo si ya sabemos que está corriendo.
    # El chequeo definitivo es atómico dentro de run_process_safely.
    if is_process_running(task_id):
        skip_msg = (
            f"[{timezone.now()}] Omitiendo ejecución de '{process.name}' - "
            f"el proceso ya está en ejecución."
        )
        print(skip_msg)
        return skip_msg

    # Verificar restricciones de horario (solo aplica a frecuencias MINUTOS / HORAS).
    current_time = timezone.localtime(timezone.now()).time()
    scheduled_tasks = ScheduledTask.objects.filter(
        process=process,
        activo=True,
        frecuencia__in=['MINUTOS', 'HORAS'],
    )
    for tarea in scheduled_tasks:
        if tarea.hora_inicio and tarea.hora_fin:
            if not (tarea.hora_inicio <= current_time <= tarea.hora_fin):
                skip_msg = (
                    f"[{timezone.now()}] Omitiendo ejecución de '{process.name}' - "
                    f"fuera del horario permitido ({tarea.hora_inicio} - {tarea.hora_fin}). "
                    f"Hora actual: {current_time.strftime('%H:%M')}"
                )
                print(skip_msg)
                return skip_msg

    print(
        f"[{timezone.now()}] Iniciando tarea programada para el proceso: "
        f"'{process.name}' (ID: {task_id})"
    )

    # Ejecución sincrónica con lock atómico a nivel de BD.
    return run_process_safely(task_id)
