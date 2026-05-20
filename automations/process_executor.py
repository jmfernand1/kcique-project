import subprocess
import threading
import os
import shlex
from datetime import timedelta
from django.utils import timezone
from .models import AutomatedProcess, ProcessLog

# Semáforo para limitar el número máximo de procesos concurrentes DENTRO de
# este proceso de Python. (No protege entre procesos distintos del SO.)
MAX_CONCURRENT_PROCESSES = 4
process_semaphore = threading.Semaphore(MAX_CONCURRENT_PROCESSES)

# Tiempo (en minutos) tras el cual un lock que sigue activo se considera
# obsoleto. Esto sucede, por ejemplo, cuando el worker que ejecutaba la tarea
# murió sin liberar el lock. Se usa solo cuando el proceso no define su
# propio campo `max_runtime_minutes`.
DEFAULT_STALE_LOCK_TIMEOUT_MINUTES = 180


# ---------------------------------------------------------------------------
#  LOCK DE EJECUCIÓN A NIVEL DE BASE DE DATOS
# ---------------------------------------------------------------------------
#  El problema original era que el control de "proceso en ejecución" se hacía
#  con un `set()` en memoria. Django-Q ejecuta las tareas en procesos worker
#  independientes, y la web corre en otro proceso aún. Cada proceso tenía su
#  propio `set()`, por lo que un worker no "veía" que otro worker (o la web)
#  ya estaba ejecutando la misma tarea -> ejecución duplicada.
#
#  La solución usa la BASE DE DATOS (compartida por todos los procesos) como
#  lock. La operación clave es un UPDATE condicional atómico: solo UNA llamada
#  conseguirá cambiar la fila de is_running=False a is_running=True; el resto
#  recibirá 0 filas afectadas y sabrá que debe omitir la ejecución.
# ---------------------------------------------------------------------------

def _release_stale_lock(process_id):
    """
    Libera el lock de un proceso si lleva activo más tiempo del permitido.
    Esto recupera el sistema cuando un worker murió sin liberar el lock.
    """
    now = timezone.now()
    for proc in AutomatedProcess.objects.filter(id=process_id, is_running=True):
        timeout = proc.max_runtime_minutes or DEFAULT_STALE_LOCK_TIMEOUT_MINUTES
        is_stale = (
            proc.running_since is None
            or proc.running_since < now - timedelta(minutes=timeout)
        )
        if is_stale:
            # Se vuelve a filtrar por running_since para no pisar un lock que
            # otro proceso pudiera haber tomado entre la lectura y el update.
            released = AutomatedProcess.objects.filter(
                id=process_id, is_running=True, running_since=proc.running_since
            ).update(is_running=False, running_since=None)
            if released:
                print(f"[{now}] Lock obsoleto liberado para el proceso {process_id}.")


def claim_process(process_id):
    """
    Intenta adquirir, de forma ATÓMICA y a nivel de BASE DE DATOS, el lock de
    ejecución del proceso.

    Retorna True si se obtuvo el lock (se puede ejecutar),
    o False si el proceso ya estaba en ejecución (se debe omitir).
    """
    _release_stale_lock(process_id)
    claimed = AutomatedProcess.objects.filter(
        id=process_id, is_running=False
    ).update(is_running=True, running_since=timezone.now())
    return claimed == 1


def release_process(process_id):
    """Libera el lock de ejecución del proceso para futuras ejecuciones."""
    AutomatedProcess.objects.filter(id=process_id).update(
        is_running=False, running_since=None
    )


def is_process_running(process_id):
    """
    Verifica en la base de datos si un proceso está actualmente en ejecución.
    Antes de responder, libera locks obsoletos para no reportar falsos positivos.
    """
    _release_stale_lock(process_id)
    return AutomatedProcess.objects.filter(id=process_id, is_running=True).exists()


# --- Alias retrocompatibles con la API anterior basada en memoria ---
def mark_process_as_running(process_id):
    """Compatibilidad: equivale ahora a claim_process()."""
    return claim_process(process_id)


def mark_process_as_finished(process_id):
    """Compatibilidad: equivale ahora a release_process()."""
    release_process(process_id)


def execute_script(process_id):
    """
    Ejecuta el script asociado a un AutomatedProcess y registra su log.
    Esta función está diseñada para ser ejecutada en un hilo separado.
    Asume que el lock del proceso YA fue adquirido por el llamador
    (run_process_threaded). Siempre libera el lock al terminar.
    """
    try:
        process_instance = AutomatedProcess.objects.get(id=process_id)
    except AutomatedProcess.DoesNotExist:
        print(f"Error: Proceso con id {process_id} no encontrado.")
        release_process(process_id)
        return

    log_entry = ProcessLog.objects.create(
        process=process_instance,
        status='STARTED'
    )

    print(f"Intentando adquirir semáforo para el proceso: {process_instance.name}")

    try:
        with process_semaphore:
            print(f"Semáforo adquirido para el proceso: {process_instance.name}")
            log_entry.status = 'RUNNING'
            log_entry.save()

            process_instance.last_run_time = timezone.now()
            # update_fields evita que un save() completo pise los campos del lock.
            process_instance.save(update_fields=['last_run_time'])

            output = []
            error_output = []
            final_status = 'FAILED' # Asumir fallo hasta que se complete con éxito

            try:
                # Construir el comando
                script_path = process_instance.script_path
                python_executable = 'python' # O 'python3' dependiendo del sistema/entorno

                # Si hay un entorno virtual especificado, activarlo
                if process_instance.virtual_env_path:
                    # Esto es una simplificación. Activar un venv para un subproceso puede ser complejo.
                    # Una forma común es llamar directamente al python del venv.
                    python_executable = os.path.join(process_instance.virtual_env_path, 'bin', 'python')
                    if not os.path.exists(python_executable):
                        # Intenta con Scripts para Windows
                        python_executable_win = os.path.join(process_instance.virtual_env_path, 'Scripts', 'python.exe')
                        if os.path.exists(python_executable_win):
                            python_executable = python_executable_win
                        else:
                            error_message = f"Python ejecutable no encontrado en el venv: {process_instance.virtual_env_path}"
                            print(error_message)
                            output.append(error_message)
                            log_entry.status = 'FAILED'
                            log_entry.output_log = "\n".join(output)
                            log_entry.end_time = timezone.now()
                            log_entry.save()
                            process_instance.last_run_status = 'Failed'
                            process_instance.save(update_fields=['last_run_status'])
                            return


                command = [python_executable, script_path]

                # Añadir argumentos si es necesario (esto requeriría modificar el modelo)
                # command.extend(process_instance.arguments.split())

                print(f"Ejecutando comando: {' '.join(command)}")
                # Usar shlex.split si el comando es una cadena compleja, pero aquí es una lista.

                # Entorno del subproceso
                env = os.environ.copy()
                if process_instance.virtual_env_path:
                     # Modificar el PATH para que incluya el bin del venv
                     # Esto es más robusto que solo llamar al python del venv para algunos scripts
                    venv_bin_path = os.path.join(process_instance.virtual_env_path, 'bin')
                    if os.name == 'nt': # Windows
                        venv_bin_path = os.path.join(process_instance.virtual_env_path, 'Scripts')

                    current_path = env.get('PATH', '')
                    if venv_bin_path not in current_path:
                        env['PATH'] = f"{venv_bin_path}{os.pathsep}{current_path}"
                    # Para algunos venvs, también es útil VIRTUAL_ENV
                    env['VIRTUAL_ENV'] = process_instance.virtual_env_path


                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    env=env
                )

                # Captura de output en tiempo real (simplificado)
                # Para un log en tiempo real más robusto en la UI, se necesitaría WebSockets o polling.
                for line in iter(process.stdout.readline, ''):
                    print(line, end='')
                    output.append(line.strip())
                    # Podríamos guardar parcialmente el log aquí si es muy largo o se quiere ver "en vivo"
                    # log_entry.output_log = "\n".join(output)
                    # log_entry.save()

                for line in iter(process.stderr.readline, ''):
                    print(f"Error: {line}", end='')
                    error_output.append(line.strip())

                process.stdout.close()
                process.stderr.close()
                process.wait()

                if process.returncode == 0:
                    final_status = 'SUCCESS'
                    process_instance.last_run_status = 'Success'
                else:
                    final_status = 'FAILED'
                    process_instance.last_run_status = f'Failed (Code: {process.returncode})'
                    output.append(f"--- ERRORES ({process.returncode}) ---")
                    output.extend(error_output)


            except Exception as e:
                print(f"Excepción durante la ejecución del script {process_instance.name}: {e}")
                output.append(f"Error interno del sistema al ejecutar el script: {str(e)}")
                final_status = 'FAILED'
                process_instance.last_run_status = 'Failed (Exception)'

            finally:
                log_entry.output_log = "\n".join(output)
                log_entry.status = final_status
                log_entry.end_time = timezone.now()
                log_entry.save()
                process_instance.save(update_fields=['last_run_status', 'last_run_time'])
                print(f"Proceso {process_instance.name} finalizado con estado: {final_status}. Semáforo liberado.")

    finally:
        # Siempre liberar el lock del proceso, incluso si hay excepciones,
        # para que pueda volver a ejecutarse en el futuro.
        release_process(process_id)


def run_process_threaded(process_id):
    """
    Inicia la ejecución de un proceso en un nuevo hilo.
    Antes de iniciar, adquiere de forma atómica (a nivel de BD) el lock del
    proceso. Si el proceso ya está en ejecución, se cancela la ejecución
    duplicada SIN lanzar el hilo.
    """
    # Adquirir el lock de forma atómica. Si falla, el proceso ya corría.
    if not claim_process(process_id):
        msg = f"El proceso {process_id} ya está en ejecución. Ejecución duplicada cancelada."
        print(msg)
        return msg

    try:
        thread = threading.Thread(target=execute_script, args=(process_id,))
        thread.start()
    except Exception as e:
        # Si no se pudo lanzar el hilo, liberar el lock para no dejarlo colgado.
        release_process(process_id)
        msg = f"Error al iniciar el hilo del proceso {process_id}: {e}"
        print(msg)
        return msg

    print(f"Proceso {process_id} enviado a ejecución en un hilo.")
    return f"Proceso {process_id} iniciado correctamente."
    # No se une al hilo aquí para permitir que la solicitud principal (ej. HTTP) termine rápido.
    # El hilo continuará en segundo plano.
