from .process_executor import run_process_threaded
from .models import AutomatedProcess
from django.utils import timezone

def execute_automated_process(*args, **kwargs):
    """
    Tarea de Django-Q que busca un AutomatedProcess por su ID
    y lo ejecuta usando el process_executor.
    Acepta kwargs para ser compatible con la forma en que django-q invoca las tareas.
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