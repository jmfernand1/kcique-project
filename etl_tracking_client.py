"""
Cliente Python para interactuar con la API de Tracking de Dexter.
Este archivo puede estar en tu proyecto ETL externo (sin Django).

Requisitos:
    pip install requests

Uso:
    from etl_tracking_client import ETLTrackingClient
    
    client = ETLTrackingClient("http://localhost:8000/dexter/api")
    ejecucion_id = client.iniciar_ejecucion_desembolso(total=100)
    # ... tu lógica ETL ...
    client.completar_ejecucion(ejecucion_id)
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime


class ETLTrackingClient:
    """Cliente para interactuar con la API de Tracking"""
    
    def __init__(self, base_url: str = "http://localhost:8000/dexter/api"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    # ==================== EJECUCIONES ====================
    
    def iniciar_ejecucion_desembolso(self, total_registros: int, descripcion: str = None) -> int:
        """
        Inicia una nueva ejecución de ETL de desembolsos.
        
        Returns:
            ID de la ejecución creada
        """
        data = {
            'tipo_proceso': 'DESEMBOLSO',
            'estado': 'EN_PROGRESO',
            'total_registros': total_registros,
            'descripcion': descripcion or f'ETL Desembolso {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }
        
        response = self.session.post(f'{self.base_url}/ejecuciones/', json=data)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Ejecución de desembolso iniciada: ID {result['id']}")
        return result['id']
    
    def iniciar_ejecucion_garantia(self, total_registros: int, descripcion: str = None) -> int:
        """Inicia una nueva ejecución de ETL de garantías"""
        data = {
            'tipo_proceso': 'GARANTIA',
            'estado': 'EN_PROGRESO',
            'total_registros': total_registros,
            'descripcion': descripcion or f'ETL Garantía {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        }
        
        response = self.session.post(f'{self.base_url}/ejecuciones/', json=data)
        response.raise_for_status()
        result = response.json()
        print(f"✅ Ejecución de garantía iniciada: ID {result['id']}")
        return result['id']
    
    def obtener_ejecuciones_pendientes(self, tipo_proceso: str = None) -> List[Dict]:
        """
        Obtiene ejecuciones que no están completadas.
        
        Args:
            tipo_proceso: 'DESEMBOLSO' o 'GARANTIA' (opcional)
        """
        url = f'{self.base_url}/ejecuciones/pendientes/'
        params = {'tipo_proceso': tipo_proceso} if tipo_proceso else {}
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def obtener_ejecucion(self, ejecucion_id: int) -> Dict:
        """Obtiene los detalles de una ejecución"""
        response = self.session.get(f'{self.base_url}/ejecuciones/{ejecucion_id}/')
        response.raise_for_status()
        return response.json()
    
    def obtener_progreso(self, ejecucion_id: int) -> Dict:
        """Obtiene el progreso detallado de una ejecución"""
        response = self.session.get(f'{self.base_url}/ejecuciones/{ejecucion_id}/progreso/')
        response.raise_for_status()
        return response.json()
    
    def completar_ejecucion(self, ejecucion_id: int):
        """Marca una ejecución como completada"""
        response = self.session.post(f'{self.base_url}/ejecuciones/{ejecucion_id}/completar/')
        response.raise_for_status()
        print(f"✅ Ejecución {ejecucion_id} marcada como completada")
        return response.json()
    
    def fallar_ejecucion(self, ejecucion_id: int, mensaje_error: str = None):
        """Marca una ejecución como fallida"""
        data = {'mensaje_error': mensaje_error} if mensaje_error else {}
        response = self.session.post(f'{self.base_url}/ejecuciones/{ejecucion_id}/fallar/', json=data)
        response.raise_for_status()
        print(f"❌ Ejecución {ejecucion_id} marcada como fallida")
        return response.json()
    
    # ==================== PROCESOS DESEMBOLSO ====================
    
    def crear_proceso_desembolso(self, ejecucion_id: int, desembolso_id: int) -> int:
        """
        Crea un nuevo proceso de tracking para un desembolso.
        
        Returns:
            ID del proceso creado
        """
        data = {
            'ejecucion': ejecucion_id,
            'desembolso': desembolso_id,
            'etapa_actual': 'PENDIENTE'
        }
        
        response = self.session.post(f'{self.base_url}/procesos-desembolso/', json=data)
        response.raise_for_status()
        return response.json()['id']
    
    def avanzar_etapa_desembolso(self, proceso_id: int, etapa: str, datos_etapa: Dict = None):
        """
        Avanza un proceso de desembolso a la siguiente etapa.
        
        Args:
            proceso_id: ID del proceso
            etapa: Nombre de la etapa (GRABAR_CARGOS_FIJOS, DESEMBOLSO, etc.)
            datos_etapa: Datos adicionales de la etapa (opcional)
        """
        data = {'etapa': etapa}
        if datos_etapa:
            data['datos_etapa'] = datos_etapa
        
        response = self.session.post(
            f'{self.base_url}/procesos-desembolso/{proceso_id}/avanzar_etapa/',
            json=data
        )
        response.raise_for_status()
        print(f"  ✓ Etapa {etapa} completada")
        return response.json()
    
    def marcar_error_desembolso(self, proceso_id: int, mensaje_error: str):
        """Marca un proceso de desembolso como error"""
        data = {'mensaje_error': mensaje_error}
        response = self.session.post(
            f'{self.base_url}/procesos-desembolso/{proceso_id}/marcar_error/',
            json=data
        )
        response.raise_for_status()
        print(f"  ❌ Error registrado: {mensaje_error}")
        return response.json()
    
    def completar_proceso_desembolso(self, proceso_id: int):
        """Marca un proceso de desembolso como completado"""
        response = self.session.post(
            f'{self.base_url}/procesos-desembolso/{proceso_id}/completar/'
        )
        response.raise_for_status()
        print(f"  ✅ Proceso completado")
        return response.json()
    
    def obtener_procesos_desembolso_pendientes(self, ejecucion_id: int) -> List[Dict]:
        """Obtiene todos los procesos de desembolso pendientes de una ejecución"""
        response = self.session.get(
            f'{self.base_url}/procesos-desembolso/',
            params={'ejecucion': ejecucion_id}
        )
        response.raise_for_status()
        resultados = response.json()['results']
        # Filtrar solo los que no están completados
        return [p for p in resultados if p['etapa_actual'] != 'COMPLETADO']
    
    # ==================== PROCESOS GARANTÍA ====================
    
    def crear_proceso_garantia(self, ejecucion_id: int, garantia_id: int) -> int:
        """Crea un nuevo proceso de tracking para una garantía"""
        data = {
            'ejecucion': ejecucion_id,
            'garantia': garantia_id,
            'etapa_actual': 'PENDIENTE'
        }
        
        response = self.session.post(f'{self.base_url}/procesos-garantia/', json=data)
        response.raise_for_status()
        return response.json()['id']
    
    def avanzar_etapa_garantia(self, proceso_id: int, etapa: str, datos_etapa: Dict = None):
        """Avanza un proceso de garantía a la siguiente etapa"""
        data = {'etapa': etapa}
        if datos_etapa:
            data['datos_etapa'] = datos_etapa
        
        response = self.session.post(
            f'{self.base_url}/procesos-garantia/{proceso_id}/avanzar_etapa/',
            json=data
        )
        response.raise_for_status()
        print(f"  ✓ Etapa {etapa} completada")
        return response.json()
    
    def marcar_error_garantia(self, proceso_id: int, mensaje_error: str):
        """Marca un proceso de garantía como error"""
        data = {'mensaje_error': mensaje_error}
        response = self.session.post(
            f'{self.base_url}/procesos-garantia/{proceso_id}/marcar_error/',
            json=data
        )
        response.raise_for_status()
        print(f"  ❌ Error registrado: {mensaje_error}")
        return response.json()
    
    def completar_proceso_garantia(self, proceso_id: int):
        """Marca un proceso de garantía como completado"""
        response = self.session.post(
            f'{self.base_url}/procesos-garantia/{proceso_id}/completar/'
        )
        response.raise_for_status()
        print(f"  ✅ Proceso completado")
        return response.json()
    
    def obtener_procesos_garantia_pendientes(self, ejecucion_id: int) -> List[Dict]:
        """Obtiene todos los procesos de garantía pendientes de una ejecución"""
        response = self.session.get(
            f'{self.base_url}/procesos-garantia/',
            params={'ejecucion': ejecucion_id}
        )
        response.raise_for_status()
        resultados = response.json()['results']
        return [p for p in resultados if p['etapa_actual'] != 'COMPLETADO']


# ==================== EJEMPLO DE USO ====================

def ejemplo_etl_desembolso_con_tracking():
    """Ejemplo de cómo usar el cliente en tu ETL de desembolsos"""
    
    print("=" * 70)
    print("EJEMPLO: ETL DE DESEMBOLSOS CON TRACKING")
    print("=" * 70)
    
    # Inicializar cliente
    client = ETLTrackingClient("http://localhost:8000/dexter/api")
    
    # 1. Verificar si hay una ejecución pendiente
    pendientes = client.obtener_ejecuciones_pendientes('DESEMBOLSO')
    
    if pendientes:
        print(f"\n🔄 Encontrada ejecución pendiente")
        ejecucion_id = pendientes[0]['id']
        print(f"   Retomando ejecución ID: {ejecucion_id}")
        
        # Obtener procesos pendientes
        procesos_pendientes = client.obtener_procesos_desembolso_pendientes(ejecucion_id)
        print(f"   Procesos pendientes: {len(procesos_pendientes)}")
    else:
        # 2. Iniciar nueva ejecución
        ejecucion_id = client.iniciar_ejecucion_desembolso(
            total_registros=3,
            descripcion="ETL de desembolsos - Ejemplo"
        )
    
    # 3. Simulación de datos (en tu ETL real, estos vendrían de tu fuente de datos)
    desembolsos_ejemplo = [
        {'id': 1, 'referencia': 'DES-001'},
        {'id': 2, 'referencia': 'DES-002'},
        {'id': 3, 'referencia': 'DES-003'},
    ]
    
    for desembolso_data in desembolsos_ejemplo:
        desembolso_id = desembolso_data['id']
        referencia = desembolso_data['referencia']
        
        print(f"\n🔄 Procesando Desembolso {referencia}")
        
        try:
            # Crear proceso de tracking
            proceso_id = client.crear_proceso_desembolso(ejecucion_id, desembolso_id)
            
            # ETAPA 1: Grabar cargos fijos
            print("  → Grabando cargos fijos...")
            # Aquí va tu lógica real
            client.avanzar_etapa_desembolso(proceso_id, 'GRABAR_CARGOS_FIJOS', {
                'cargos_creados': 2
            })
            
            # ETAPA 2: Desembolso
            print("  → Ejecutando desembolso...")
            # Aquí va tu lógica real
            client.avanzar_etapa_desembolso(proceso_id, 'DESEMBOLSO', {
                'monto': 10000000
            })
            
            # ETAPA 3: Fraccionar
            print("  → Fraccionando...")
            # Aquí va tu lógica real
            client.avanzar_etapa_desembolso(proceso_id, 'FRACCIONAR', {
                'tramos': 2
            })
            
            # ETAPA 4: Seleccionar pago
            print("  → Seleccionando forma de pago...")
            # Aquí va tu lógica real
            client.avanzar_etapa_desembolso(proceso_id, 'SELECCIONAR_PAGO')
            
            # ETAPA 5: Autorizar
            print("  → Autorizando...")
            # Aquí va tu lógica real
            client.avanzar_etapa_desembolso(proceso_id, 'AUTORIZAR')
            
            # Marcar como completado
            client.completar_proceso_desembolso(proceso_id)
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            client.marcar_error_desembolso(proceso_id, str(e))
    
    # 4. Finalizar ejecución
    progreso = client.obtener_progreso(ejecucion_id)
    print(f"\n📊 Progreso final: {progreso['progreso_porcentaje']}%")
    print(f"   Exitosos: {progreso['registros_exitosos']}")
    print(f"   Fallidos: {progreso['registros_fallidos']}")
    
    client.completar_ejecucion(ejecucion_id)
    print("\n✅ ETL finalizado")
    print("=" * 70)


if __name__ == "__main__":
    print("\n🚀 Cliente de Tracking API para ETL\n")
    print("⚠️  Asegúrate de que el servidor Django esté corriendo:")
    print("   python manage.py runserver\n")
    
    input("Presiona Enter para ejecutar el ejemplo...")
    
    try:
        ejemplo_etl_desembolso_con_tracking()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: No se pudo conectar al servidor.")
        print("   Asegúrate de que Django esté corriendo en http://localhost:8000")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")

