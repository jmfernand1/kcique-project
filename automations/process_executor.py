import subprocess
import os
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import AutomatedProcess, ProcessLog

# Tiempo (en minutos) tras el cual se considera que un lock quedó "rancio"
# (por ejemplo si el worker que adquirió el lock fue terminado abruptamente).
# Si el lock supera este tiempo, se libera y se permite una nueva ejecución.
STALE_LOCK_AFTER_MINUTES = 180


def is_process_running(process_id):
    """
    Verifica (a nivel de base de datos) si un proceso está actualmente en ejecución.
    Esta consulta es válida para todos los workers de Django Q porque consulta la BD,
    no una estructura en memoria local del proceso.
    """
    try:
        return AutomatedProcess.objects.filter(id=process_id, is_running=True).exists()
    except Exception:
        return False


def acquire_run_lock(process_id):
    """
    Intenta adquirir el lock de ejecución de un proceso de forma ATÓMICA usando
    select_for_update. Esto garantiza que dos workers (procesos) o threads que
    compitan por el mismo proceso no puedan ambos pasar el chequeo.

    Retorna una tupla (acquired: bool, message: str).
    """
    try:
        with transaction.atomic():
            try:
                process = AutomatedProcess.objects.select_for_update().get(id=process_id)
            except AutomatedProcess.DoesNotExist:
                return False, f"Proceso con ID {process_id} no existe."

            if process.is_running:
                # Si el lock está marcado como running pero pasó demasiado tiempo,
                # se considera rancio (probablemente el worker murió sin liberar).
                stale_threshold = timezone.now() - timedelta(minutes=STALE_LOCK_AFTER_MINUTES)
                if process.running_started_at and process.running_started_at < stale_threshold:
                    print(
                        f"[{timezone.now()}] Lock rancio detectado para '{process.name}' "
                        f"(adquirido el {process.running_started_at}). Se libera y se reintenta."
                    )
                else:
                    return False, (
                        f"El proceso '{process.name}' ya está en ejecución "
                        f"(desde {process.running_started_at})."
                    )

            process.is_running = True
            process.running_started_at = timezone.now()
            process.save(update_fields=['is_running', 'running_started_at'])
            return True, f"Lock adquirido para '{process.name}'."
    except Exception as e:
        return False, f"Error al adquirir lock para proceso {process_id}: {e}"


def release_run_lock(process_id):
    """
    Libera el lock de ejecución de un proceso. Idempotente.
    """
    try:
        AutomatedProcess.objects.filter(id=process_id).update(
            is_running=False,
            running_started_at=None,
        )
    except Exception as e:
        print(f"Error al liberar lock para proceso {process_id}: {e}")


def _build_command_and_env(process_instance):
    """
    Construye el comando y el entorno para ejecutar el script asociado al proceso.
    Retorna (command_list, env_dict, error_message_or_None).
    """
    script_path = process_instance.script_path
    python_executable = 'python'

    if process_instance.virtual_env_path:
        python_executable = os.path.join(process_instance.virtual_env_path, 'bin', 'python')
        if not os.path.exists(python_executable):
            python_executable_win = os.path.join(
                process_instance.virtual_env_path, 'Scripts', 'python.exe'
            )
            if os.path.exists(python_executable_win):
                python_executable = python_executable_win
            else:
                return None, None, (
                    f"Python ejecutable no encontrado en el venv: "
                    f"{process_instance.virtual_env_path}"
                )

    command = [python_executable, script_path]

    env = os.environ.copy()
    if process_instance.virtual_env_path:
        if os.name == 'nt':
            venv_bin_path = os.path.join(process_instance.virtual_env_path, 'Scripts')
        else:
            venv_bin_path = os.path.join(process_instance.virtual_env_path, 'bin')

        current_path = env.get('PATH', '')
        if venv_bin_path not in current_path:
            env['PATH'] = f"{venv_bin_path}{os.pathsep}{current_path}"
        env['VIRTUAL_ENV'] = process_instance.virtual_env_path

    return command, env, None


def execute_script(process_id):
    """
    Ejecuta el script asociado a un AutomatedProcess de forma SINCRÓNICA y registra su log.

    IMPORTANTE: esta función debe ejecutarse de forma síncrona dentro del worker que
    la invoca (un worker de Django Q o un thread del servidor web). No lanza un thread
    extra; así el worker queda ocupado durante toda la duración del script y Django Q
    no entrega ejecuciones duplicadas mientras el script corre.

    El lock a nivel de BD ya se adquirió antes de llamar a esta función (en
    run_process_safely). Aquí solo nos aseguramos de liberarlo en el `finally`.
    """
    log_entry = None
    final_status = 'FAILED'
    output = []
    error_output = []

    try:
        try:
            process_instance = AutomatedProcess.objects.get(id=process_id)
        except AutomatedProcess.DoesNotExist:
            print(f"Error: Proceso con id {process_id} no encontrado.")
            return

        log_entry = ProcessLog.objects.create(
            process=process_instance,
            status='RUNNING',
        )

        process_instance.last_run_time = timezone.now()
        process_instance.save(update_fields=['last_run_time'])

        command, env, build_error = _build_command_and_env(process_instance)
        if build_error:
            print(build_error)
            output.append(build_error)
            process_instance.last_run_status = 'Failed'
            process_instance.save(update_fields=['last_run_status'])
            return

        print(f"[{timezone.now()}] Ejecutando comando: {' '.join(command)}")

        try:
            proc = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            for line in iter(proc.stdout.readline, ''):
                print(line, end='')
                output.append(line.rstrip())

            for line in iter(proc.stderr.readline, ''):
                print(f"Error: {line}", end='')
                error_output.append(line.rstrip())

            proc.stdout.close()
            proc.stderr.close()
            proc.wait()

            if proc.returncode == 0:
                final_status = 'SUCCESS'
                process_instance.last_run_status = 'Success'
            else:
                final_status = 'FAILED'
                process_instance.last_run_status = f'Failed (Code: {proc.returncode})'
                output.append(f"--- ERRORES ({proc.returncode}) ---")
                output.extend(error_output)

        except Exception as e:
            print(f"Excepción durante la ejecución del script {process_instance.name}: {e}")
            output.append(f"Error interno del sistema al ejecutar el script: {str(e)}")
            final_status = 'FAILED'
            process_instance.last_run_status = 'Failed (Exception)'

        finally:
            if log_entry is not None:
                log_entry.output_log = "\n".join(output)
                log_entry.status = final_status
                log_entry.end_time = timezone.now()
                log_entry.save()
            try:
                process_instance.save(update_fields=['last_run_status'])
            except Exception:
                pass
            print(
                f"[{timezone.now()}] Proceso {process_instance.name} "
                f"finalizado con estado: {final_status}."
            )

    finally:
        # Siempre liberar el lock, incluso ante excepciones inesperadas.
        release_run_lock(process_id)


def run_process_safely(process_id):
    """
    Adquiere el lock a nivel de BD y ejecuta el script de forma sincrónica.

    Este es el ÚNICO punto de entrada que debe usarse para correr un proceso, tanto
    desde una tarea programada de Django Q como desde una ejecución manual disparada
    vía async_task. Si el proceso ya está corriendo (en cualquier worker), se cancela
    la ejecución duplicada.
    """
    acquired, msg = acquire_run_lock(process_id)
    if not acquired:
        print(f"[{timezone.now()}] Ejecución cancelada: {msg}")
        return msg

    print(f"[{timezone.now()}] {msg} Iniciando ejecución sincrónica.")
    execute_script(process_id)
    return f"Proceso {process_id} ejecutado."


def run_process_threaded(process_id):
    """
    Compatibilidad hacia atrás. Antes lanzaba un thread; ahora delega a Django Q
    vía async_task para que la ejecución viaje por la cola y respete el lock de BD.

    Si Django Q no está disponible por algún motivo, cae a la ejecución sincrónica
    (con lock) en el proceso actual.
    """
    try:
        from django_q.tasks import async_task
        async_task('automations.process_executor.run_process_safely', process_id)
        msg = f"Proceso {process_id} encolado en Django Q."
        print(f"[{timezone.now()}] {msg}")
        return msg
    except Exception as e:
        print(
            f"[{timezone.now()}] No se pudo encolar en Django Q ({e}). "
            f"Se ejecutará sincrónicamente en este proceso."
        )
        return run_process_safely(process_id)
