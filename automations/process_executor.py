import subprocess
import threading
import os
import shlex
from django.utils import timezone
from .models import AutomatedProcess, ProcessLog

# Semáforo para limitar el número máximo de procesos concurrentes
MAX_CONCURRENT_PROCESSES = 4
process_semaphore = threading.Semaphore(MAX_CONCURRENT_PROCESSES)

def execute_script(process_id):
    """
    Ejecuta el script asociado a un AutomatedProcess y registra su log.
    Esta función está diseñada para ser ejecutada en un hilo separado.
    """
    try:
        process_instance = AutomatedProcess.objects.get(id=process_id)
    except AutomatedProcess.DoesNotExist:
        print(f"Error: Proceso con id {process_id} no encontrado.")
        return

    log_entry = ProcessLog.objects.create(
        process=process_instance,
        status='STARTED'
    )

    print(f"Intentando adquirir semáforo para el proceso: {process_instance.name}")
    with process_semaphore:
        print(f"Semáforo adquirido para el proceso: {process_instance.name}")
        log_entry.status = 'RUNNING'
        log_entry.save()

        process_instance.last_run_time = timezone.now()
        process_instance.save()

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
                        process_instance.save()
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
            process_instance.save()
            print(f"Proceso {process_instance.name} finalizado con estado: {final_status}. Semáforo liberado.")

def run_process_threaded(process_id):
    """
    Inicia la ejecución de un proceso en un nuevo hilo.
    """
    thread = threading.Thread(target=execute_script, args=(process_id,))
    thread.start()
    print(f"Proceso {process_id} enviado a ejecución en un hilo.")
    # No se une al hilo aquí para permitir que la solicitud principal (ej. HTTP) termine rápido.
    # El hilo continuará en segundo plano.

# Ejemplo de cómo se podría llamar (esto iría en una vista o un comando de gestión)
# if __name__ == '__main__':
#     # Esto es solo para prueba y no se ejecutará directamente así en Django.
#     # Configurar Django primero si se prueba fuera del manage.py
#     # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kcique_project.settings')
#     # import django
#     # django.setup()
#     
#     # Crear un proceso de prueba si no existe (requiere acceso a DB y modelos)
#     # test_process, created = AutomatedProcess.objects.get_or_create(
#     # name='Test Script', 
#     # script_path='path/to/your/test_script.py' # CAMBIAR ESTO
#     # )
#     # run_process_threaded(test_process.id) 