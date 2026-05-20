import requests
import json

# URL base de la API
BASE_URL = 'http://127.0.0.1:8000/adagio/api/'

def imprimir_respuesta(response):
    """Función auxiliar para imprimir la respuesta de la API de forma legible."""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=4))
    except json.JSONDecodeError:
        print("Response Text:")
        print(response.text)
    print("-" * 40)

def obtener_casos():
    """Obtiene la lista de todos los casos."""
    print(">>> Obteniendo todos los casos...")
    try:
        response = requests.get(f"{BASE_URL}casos/")
        response.raise_for_status()  # Lanza un error para códigos de estado 4xx/5xx
        imprimir_respuesta(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener casos: {e}")

def obtener_casos_pendientes():
    """Obtiene solo los casos con estado 'PENDIENTE'."""
    print(">>> Obteniendo casos pendientes...")
    try:
        response = requests.get(f"{BASE_URL}casos/", params={'estado': 'PENDIENTE'})
        response.raise_for_status()
        imprimir_respuesta(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener casos pendientes: {e}")

def crear_caso(datos_caso):
    """Crea un nuevo caso."""
    print(">>> Creando un nuevo caso...")
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.post(f"{BASE_URL}casos/", data=json.dumps(datos_caso), headers=headers)
        response.raise_for_status()
        imprimir_respuesta(response)
        return response.json() # Retorna el caso creado para poder usar su ID
    except requests.exceptions.RequestException as e:
        print(f"Error al crear el caso: {e}")
        return None

def actualizar_caso(caso_id, datos_actualizacion):
    """Actualiza un caso existente usando PATCH."""
    print(f">>> Actualizando el caso {caso_id}...")
    try:
        headers = {'Content-Type': 'application/json'}
        response = requests.patch(f"{BASE_URL}casos/{caso_id}/", data=json.dumps(datos_actualizacion), headers=headers)
        response.raise_for_status()
        imprimir_respuesta(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al actualizar el caso: {e}")

def obtener_caso_especifico(caso_id):
    """Obtiene un caso específico por su ID."""
    print(f">>> Obteniendo el caso {caso_id}...")
    try:
        response = requests.get(f"{BASE_URL}casos/{caso_id}/")
        response.raise_for_status()
        imprimir_respuesta(response)
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el caso: {e}")


if __name__ == '__main__':
    # --- Ejemplo 1: Obtener todos los casos y los pendientes ---
    obtener_casos()
    obtener_casos_pendientes()

    # --- Ejemplo 2: Crear un nuevo caso y luego actualizarlo ---
    nuevo_caso_data = {
        "cod_caso_bizagi": "CASO-PYTHON-001",
        "num_prestamo": "NP-987654",
        "docsoldv": "Documento de prueba desde Python",
        "tipo_de_cuenta": "Ahorros",
        "numcta_debito": "1234567890",
        "secuencia_cta": "1",
        "codigo_del_banco": "1020",
        "codigo_ciudad": "05001",
        "estado": "PENDIENTE",
        "proceso_creador": "script_ejemplo_api.py"
    }
    
    caso_creado = crear_caso(nuevo_caso_data)
    
    if caso_creado and 'id' in caso_creado:
        caso_id = caso_creado['id']
        print(f"Caso creado con ID: {caso_id}")
        
        # Ahora actualizamos el estado del caso que acabamos de crear
        actualizacion_data = {
            "estado": "EN_PROCESO",
            "proceso_actualizador": "script_ejemplo_api.py"
        }
        actualizar_caso(caso_id, actualizacion_data)

        # Finalmente, obtenemos el caso actualizado para verificar
        obtener_caso_especifico(caso_id) 