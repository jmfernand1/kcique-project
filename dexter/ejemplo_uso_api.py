"""
Ejemplo de uso de la API de Dexter desde un ETL en Python

Este script muestra cómo interactuar con la API REST de Dexter
para crear, leer, actualizar y eliminar registros de Desembolsos, 
Cargos Fijos y Garantías.

Requisitos:
    pip install requests
"""

import requests
import json
from datetime import date, datetime

# Configuración base
BASE_URL = "http://localhost:8000/dexter/api"
HEADERS = {
    "Content-Type": "application/json",
}

# Si usas autenticación, agrega el token aquí:
# HEADERS["Authorization"] = "Token tu_token_aqui"


class DexterAPIClient:
    """Cliente para interactuar con la API de Dexter"""
    
    def __init__(self, base_url=BASE_URL, headers=HEADERS):
        self.base_url = base_url
        self.headers = headers
    
    # =============== DESEMBOLSOS ===============
    
    def crear_desembolso(self, datos_desembolso):
        """
        Crear un nuevo desembolso
        
        Args:
            datos_desembolso (dict): Diccionario con los datos del desembolso
            
        Returns:
            dict: Respuesta del servidor con el desembolso creado
        """
        url = f"{self.base_url}/desembolsos/"
        response = requests.post(url, json=datos_desembolso, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def listar_desembolsos(self, filtros=None):
        """
        Listar todos los desembolsos (con filtros opcionales)
        
        Args:
            filtros (dict): Diccionario con filtros (ej: {'referencia': 'REF001', 'aliado': 'ALIADO1'})
            
        Returns:
            dict: Respuesta del servidor con la lista de desembolsos
        """
        url = f"{self.base_url}/desembolsos/"
        response = requests.get(url, params=filtros, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def obtener_desembolso(self, desembolso_id):
        """
        Obtener un desembolso específico por ID
        
        Args:
            desembolso_id (int): ID del desembolso
            
        Returns:
            dict: Datos del desembolso
        """
        url = f"{self.base_url}/desembolsos/{desembolso_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_desembolso(self, desembolso_id, datos_actualizados):
        """
        Actualizar un desembolso completo (PUT)
        
        Args:
            desembolso_id (int): ID del desembolso
            datos_actualizados (dict): Todos los datos del desembolso
            
        Returns:
            dict: Desembolso actualizado
        """
        url = f"{self.base_url}/desembolsos/{desembolso_id}/"
        response = requests.put(url, json=datos_actualizados, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_parcial_desembolso(self, desembolso_id, datos_parciales):
        """
        Actualizar parcialmente un desembolso (PATCH)
        
        Args:
            desembolso_id (int): ID del desembolso
            datos_parciales (dict): Solo los campos que se desean actualizar
            
        Returns:
            dict: Desembolso actualizado
        """
        url = f"{self.base_url}/desembolsos/{desembolso_id}/"
        response = requests.patch(url, json=datos_parciales, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def eliminar_desembolso(self, desembolso_id):
        """
        Eliminar un desembolso
        
        Args:
            desembolso_id (int): ID del desembolso
            
        Returns:
            bool: True si se eliminó correctamente
        """
        url = f"{self.base_url}/desembolsos/{desembolso_id}/"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True
    
    def obtener_cargos_fijos_desembolso(self, desembolso_id):
        """
        Obtener los cargos fijos asociados a un desembolso
        
        Args:
            desembolso_id (int): ID del desembolso
            
        Returns:
            list: Lista de cargos fijos
        """
        url = f"{self.base_url}/desembolsos/{desembolso_id}/cargos_fijos/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    # =============== CARGOS FIJOS ===============
    
    def crear_cargo_fijo(self, datos_cargo):
        """Crear un nuevo cargo fijo"""
        url = f"{self.base_url}/cargos-fijos/"
        response = requests.post(url, json=datos_cargo, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def listar_cargos_fijos(self, filtros=None):
        """Listar cargos fijos (con filtros opcionales)"""
        url = f"{self.base_url}/cargos-fijos/"
        response = requests.get(url, params=filtros, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def obtener_cargo_fijo(self, cargo_id):
        """Obtener un cargo fijo específico por ID"""
        url = f"{self.base_url}/cargos-fijos/{cargo_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_cargo_fijo(self, cargo_id, datos_actualizados):
        """Actualizar un cargo fijo (PUT)"""
        url = f"{self.base_url}/cargos-fijos/{cargo_id}/"
        response = requests.put(url, json=datos_actualizados, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_parcial_cargo_fijo(self, cargo_id, datos_parciales):
        """Actualizar parcialmente un cargo fijo (PATCH)"""
        url = f"{self.base_url}/cargos-fijos/{cargo_id}/"
        response = requests.patch(url, json=datos_parciales, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def eliminar_cargo_fijo(self, cargo_id):
        """Eliminar un cargo fijo"""
        url = f"{self.base_url}/cargos-fijos/{cargo_id}/"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True
    
    # =============== GARANTÍAS ===============
    
    def crear_garantia(self, datos_garantia):
        """Crear una nueva garantía"""
        url = f"{self.base_url}/garantias/"
        response = requests.post(url, json=datos_garantia, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def listar_garantias(self, filtros=None):
        """Listar garantías (con filtros opcionales)"""
        url = f"{self.base_url}/garantias/"
        response = requests.get(url, params=filtros, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def obtener_garantia(self, garantia_id):
        """Obtener una garantía específica por ID"""
        url = f"{self.base_url}/garantias/{garantia_id}/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_garantia(self, garantia_id, datos_actualizados):
        """Actualizar una garantía (PUT)"""
        url = f"{self.base_url}/garantias/{garantia_id}/"
        response = requests.put(url, json=datos_actualizados, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def actualizar_parcial_garantia(self, garantia_id, datos_parciales):
        """Actualizar parcialmente una garantía (PATCH)"""
        url = f"{self.base_url}/garantias/{garantia_id}/"
        response = requests.patch(url, json=datos_parciales, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def eliminar_garantia(self, garantia_id):
        """Eliminar una garantía"""
        url = f"{self.base_url}/garantias/{garantia_id}/"
        response = requests.delete(url, headers=self.headers)
        response.raise_for_status()
        return True


def ejemplo_uso_completo():
    """Ejemplo completo de uso de la API"""
    
    # Crear cliente
    cliente = DexterAPIClient()
    
    print("=" * 60)
    print("EJEMPLO DE USO DE LA API DE DEXTER")
    print("=" * 60)
    
    # 1. CREAR UN DESEMBOLSO
    print("\n1. Creando un desembolso...")
    datos_desembolso = {
        "referencia": "DES-2025-001",
        "obligacion": 123456789,
        "id_cliente": 987654321,
        "nit_beneficiario": 900123456,
        "aliado": "ALIADO_PRUEBA",
        "tipo_cta_destino": "Ahorros",
        "cod_tipo_cuenta_destino": 1,
        "num_cta_destino": 1234567890,
        "banco_destino": "Banco de Prueba",
        "cod_banco_destino": 51,
        "valor_desembolso": 10000000.00,
        "numero_tramos": 2,
        "plazo_tramo_1": 12,
        "tipo_tasa_tramo_1": "EA",
        "tasa_tramo_1": 15.5,
        "amortizacion_tramo_1": "FRANCESA",
        "plazo_tramo_2": 24,
        "tipo_tasa_tramo_2": "EA",
        "tasa_tramo_2": 16.5,
        "amortizacion_tramo_2": "FRANCESA",
        "dia_pago_cuota": 15
    }
    
    try:
        desembolso_creado = cliente.crear_desembolso(datos_desembolso)
        print(f"✅ Desembolso creado con ID: {desembolso_creado['id']}")
        desembolso_id = desembolso_creado['id']
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al crear desembolso: {e}")
        return
    
    # 2. CREAR UN CARGO FIJO ASOCIADO AL DESEMBOLSO
    print("\n2. Creando un cargo fijo...")
    datos_cargo = {
        "desembolso": desembolso_id,
        "codigo": "CF001",
        "nombre_cargo_fijo": "Cargo de Administración",
        "fecha_efectiva": date.today().isoformat(),
        "periodicidad": "MENSUAL",
        "valor": 50000.00
    }
    
    try:
        cargo_creado = cliente.crear_cargo_fijo(datos_cargo)
        print(f"✅ Cargo fijo creado con ID: {cargo_creado['id']}")
        cargo_id = cargo_creado['id']
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al crear cargo fijo: {e}")
    
    # 3. CREAR UNA GARANTÍA
    print("\n3. Creando una garantía...")
    datos_garantia = {
        "referencia": "DES-2025-001",
        "obligacion": 123456789,
        "id_cliente": 987654321,
        "id_garante": 987654321,
        "cod_fasecolda": "1234",
        "codigo_fasecolda": "5678",
        "color": "ROJO",
        "placa": "ABC123",
        "modelo": "2024",
        "valor_vehiculo": 50000000,
        "fecha_desembolso": date.today().isoformat()
    }
    
    try:
        garantia_creada = cliente.crear_garantia(datos_garantia)
        print(f"✅ Garantía creada con ID: {garantia_creada['id']}")
        garantia_id = garantia_creada['id']
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al crear garantía: {e}")
        return
    
    # 4. LISTAR DESEMBOLSOS
    print("\n4. Listando desembolsos...")
    try:
        desembolsos = cliente.listar_desembolsos()
        print(f"✅ Total de desembolsos: {desembolsos['count']}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al listar desembolsos: {e}")
    
    # 5. FILTRAR DESEMBOLSOS POR ALIADO
    print("\n5. Filtrando desembolsos por aliado...")
    try:
        desembolsos_filtrados = cliente.listar_desembolsos(filtros={'aliado': 'ALIADO_PRUEBA'})
        print(f"✅ Desembolsos encontrados: {desembolsos_filtrados['count']}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al filtrar desembolsos: {e}")
    
    # 6. OBTENER CARGOS FIJOS DE UN DESEMBOLSO
    print("\n6. Obteniendo cargos fijos del desembolso...")
    try:
        cargos = cliente.obtener_cargos_fijos_desembolso(desembolso_id)
        print(f"✅ Cargos fijos encontrados: {len(cargos)}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al obtener cargos fijos: {e}")
    
    # 7. ACTUALIZAR PARCIALMENTE UN DESEMBOLSO
    print("\n7. Actualizando valor del desembolso...")
    try:
        desembolso_actualizado = cliente.actualizar_parcial_desembolso(
            desembolso_id,
            {"valor_desembolso": 12000000.00}
        )
        print(f"✅ Desembolso actualizado. Nuevo valor: {desembolso_actualizado['valor_desembolso']}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al actualizar desembolso: {e}")
    
    # 8. BUSCAR GARANTÍAS POR PLACA
    print("\n8. Buscando garantías por placa...")
    try:
        garantias = cliente.listar_garantias(filtros={'placa': 'ABC123'})
        print(f"✅ Garantías encontradas: {garantias['count']}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al buscar garantías: {e}")
    
    print("\n" + "=" * 60)
    print("FIN DEL EJEMPLO")
    print("=" * 60)


def ejemplo_etl_basico():
    """
    Ejemplo de un ETL básico que:
    1. Lee datos de una fuente (simulado con diccionarios)
    2. Los transforma
    3. Los carga a través de la API
    """
    
    print("\n" + "=" * 60)
    print("EJEMPLO DE ETL BÁSICO")
    print("=" * 60)
    
    cliente = DexterAPIClient()
    
    # Simular datos de origen (podrían venir de un CSV, base de datos, etc.)
    datos_origen = [
        {
            "ref": "DES-2025-100",
            "oblig": 111111111,
            "cliente": 222222222,
            "nit_benef": 900111111,
            "partner": "PARTNER_A",
            "valor": 5000000.00
        },
        {
            "ref": "DES-2025-101",
            "oblig": 333333333,
            "cliente": 444444444,
            "nit_benef": 900222222,
            "partner": "PARTNER_B",
            "valor": 7500000.00
        }
    ]
    
    print(f"\n📥 Procesando {len(datos_origen)} registros...\n")
    
    procesados = 0
    errores = 0
    
    for idx, registro in enumerate(datos_origen, 1):
        try:
            # Transformar datos al formato de la API
            datos_transformados = {
                "referencia": registro["ref"],
                "obligacion": registro["oblig"],
                "id_cliente": registro["cliente"],
                "nit_beneficiario": registro["nit_benef"],
                "aliado": registro["partner"],
                "tipo_cta_destino": "Ahorros",
                "cod_tipo_cuenta_destino": 1,
                "num_cta_destino": 9999999999,
                "banco_destino": "Banco ETL",
                "cod_banco_destino": 99,
                "valor_desembolso": registro["valor"],
                "numero_tramos": 1,
                "plazo_tramo_1": 12,
                "tipo_tasa_tramo_1": "EA",
                "tasa_tramo_1": 15.0,
                "amortizacion_tramo_1": "FRANCESA",
                "plazo_tramo_2": 0,
                "tipo_tasa_tramo_2": "EA",
                "tasa_tramo_2": 0.0,
                "amortizacion_tramo_2": "FRANCESA"
            }
            
            # Cargar datos a través de la API
            resultado = cliente.crear_desembolso(datos_transformados)
            print(f"✅ Registro {idx}: {registro['ref']} - ID: {resultado['id']}")
            procesados += 1
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ Registro {idx}: {registro['ref']} - Error: {e}")
            errores += 1
        except Exception as e:
            print(f"❌ Registro {idx}: Error inesperado: {e}")
            errores += 1
    
    print(f"\n📊 Resumen del ETL:")
    print(f"   - Procesados exitosamente: {procesados}")
    print(f"   - Errores: {errores}")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🚀 Iniciando ejemplos de uso de la API de Dexter\n")
    print("⚠️  Asegúrate de que el servidor Django esté corriendo:")
    print("   python manage.py runserver\n")
    
    input("Presiona Enter para continuar...")
    
    # Descomentar el ejemplo que desees ejecutar:
    # ejemplo_uso_completo()
    # ejemplo_etl_basico()
    
    print("\n✅ Ejemplos completados")

