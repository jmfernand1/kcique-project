from .process_executor import run_process_threaded
from .models import AutomatedProcess, ScheduledTask
from django.utils import timezone
from datetime import time

def execute_automated_process(*args, **kwargs):
    """
    Tarea de Django-Q que busca un AutomatedProcess por su ID
    y lo ejecuta usando el process_executor.
    Acepta kwargs para ser compatible con la forma en que django-q invoca las tareas.
    Verifica el rango de horas si está configurado.
    """
    task_id = kwargs.get('task_id')
    if task_id is None:
        # Intenta obtener el ID del primer argumento posicional si no está en kwargs
        if args:
            task_id = args[0]
        else:
            error_msg = f"Error: No se pudo ejecutar la tarea programada. No se proporcionó 'task_id'."
            print(error_msg)
            return error_msg
            
    try:
        process = AutomatedProcess.objects.get(id=task_id)
        
        # Verificar si hay restricciones de horario para tareas de tipo MINUTOS o HORAS
        current_time = timezone.now().time()
        
        # Buscar tareas programadas que apliquen restricciones de horario
        scheduled_tasks = ScheduledTask.objects.filter(
            process=process,
            activo=True,
            frecuencia__in=['MINUTOS', 'HORAS']
        )
        
        # Verificar si alguna tarea tiene restricciones de horario
        for task in scheduled_tasks:
            if task.hora_inicio and task.hora_fin:
                # Verificar si la hora actual está dentro del rango permitido
                if not (task.hora_inicio <= current_time <= task.hora_fin):
                    skip_msg = f"[{timezone.now()}] Omitiendo ejecución de '{process.name}' - fuera del horario permitido ({task.hora_inicio} - {task.hora_fin}). Hora actual: {current_time.strftime('%H:%M')}"
                    print(skip_msg)
                    return skip_msg
        
        print(f"[{timezone.now()}] Iniciando tarea programada para el proceso: '{process.name}' (ID: {task_id})")
        
        # Usamos la función que ya maneja hilos y logging
        run_process_threaded(task_id)
        
        print(f"[{timezone.now()}] Tarea programada para '{process.name}' enviada a ejecución.")
        return f"Proceso '{process.name}' ejecutado exitosamente."
        
    except AutomatedProcess.DoesNotExist:
        error_msg = f"Error: No se pudo ejecutar la tarea programada. Proceso con ID {task_id} no encontrado."
        print(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Error inesperado al ejecutar la tarea programada para el proceso ID {task_id}: {e}"
        print(error_msg)
        return error_msg 