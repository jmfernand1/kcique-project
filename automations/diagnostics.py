from django.utils import timezone

def simple_test_task():
    """
    Una tarea de diagnóstico simple que solo imprime en la consola.
    """
    message = f"QCLUSTER DIAGNOSTIC PASSED at {timezone.now()}"
    print("##################################################")
    print(f"##  {message}")
    print("##################################################")
    return message 