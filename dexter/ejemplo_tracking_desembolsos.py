"""
Ejemplos completos de uso del sistema de tracking para Desembolsos.

Este archivo contiene 3 casos de uso completos que demuestran cómo usar
el sistema de tracking con etapas individuales para procesos de desembolso.

Casos de uso:
1. Proceso exitoso completo - Muestra el flujo normal sin errores
2. Proceso con error y reintento - Muestra manejo de errores y reintentos
3. Retomar ejecución fallida - Muestra cómo retomar una ejecución que falló

Requisitos:
    pip install requests

Uso:
    python dexter/ejemplo_tracking_desembolsos.py
"""

import requests
import time
from typing import List, Dict, Any, Optional

BASE_URL = "http://localhost:8000/dexter/api"


class TrackingDesembolsoClient:
    """Cliente simplificado para tracking de desembolsos"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def crear_ejecucion_con_plan(self, desembolso_ids: List[int], descripcion: str = None) -> Dict:
        """Crea una ejecución con plan completo"""
        response = self.session.post(
            f'{self.base_url}/ejecuciones/crear_con_plan/',
            json={
                'tipo_proceso': 'DESEMBOLSO',
                'total_registros': len(desembolso_ids),
                'descripcion': descripcion or f'ETL Desembolsos - {len(desembolso_ids)} registros',
                'desembolso_ids': desembolso_ids
            }
        )
        response.raise_for_status()
        return response.json()
    
    def obtener_procesos_pendientes(self, ejecucion_id: int) -> List[Dict]:
        """Obtiene procesos pendientes de una ejecución"""
        response = self.session.get(
            f'{self.base_url}/procesos-desembolso/',
            params={'ejecucion': ejecucion_id, 'estado_general': 'PENDIENTE'}
        )
        response.raise_for_status()
        return response.json().get('results', [])
    
    def obtener_siguiente_etapa(self, proceso_id: int) -> Optional[Dict]:
        """Obtiene la siguiente etapa pendiente de un proceso"""
        response = self.session.get(
            f'{self.base_url}/procesos-desembolso/{proceso_id}/siguiente_etapa/'
        )
        if response.status_code == 204:
            return None
        response.raise_for_status()
        return response.json()
    
    def iniciar_etapa(self, etapa_id: int) -> Dict:
        """Inicia una etapa"""
        response = self.session.post(
            f'{self.base_url}/etapas-proceso-desembolso/{etapa_id}/iniciar/'
        )
        response.raise_for_status()
        return response.json()
    
    def completar_etapa(self, etapa_id: int, datos_etapa: Dict = None) -> Dict:
        """Completa una etapa"""
        data = {}
        if datos_etapa:
            data['datos_etapa'] = datos_etapa
        
        response = self.session.post(
            f'{self.base_url}/etapas-proceso-desembolso/{etapa_id}/completar/',
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def marcar_error_etapa(self, etapa_id: int, mensaje_error: str, datos_etapa: Dict = None) -> Dict:
        """Marca una etapa como error"""
        data = {'mensaje_error': mensaje_error}
        if datos_etapa:
            data['datos_etapa'] = datos_etapa
        
        response = self.session.post(
            f'{self.base_url}/etapas-proceso-desembolso/{etapa_id}/marcar_error/',
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def reintentar_etapa(self, etapa_id: int) -> Dict:
        """Reintenta una etapa que falló"""
        response = self.session.post(
            f'{self.base_url}/etapas-proceso-desembolso/{etapa_id}/reintentar/'
        )
        response.raise_for_status()
        return response.json()
    
    def obtener_progreso(self, ejecucion_id: int) -> Dict:
        """Obtiene el progreso de una ejecución"""
        response = self.session.get(
            f'{self.base_url}/ejecuciones/{ejecucion_id}/progreso/'
        )
        response.raise_for_status()
        return response.json()
    
    def completar_ejecucion(self, ejecucion_id: int) -> Dict:
        """Completa una ejecución"""
        response = self.session.post(
            f'{self.base_url}/ejecuciones/{ejecucion_id}/completar/'
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# FUNCIONES DE SIMULACIÓN DE LÓGICA ETL
# ============================================================================

def simular_grabar_cargos_fijos(desembolso_id: int) -> Dict[str, Any]:
    """Simula la lógica de grabar cargos fijos"""
    print(f"    📝 Grabando cargos fijos para desembolso {desembolso_id}...")
    time.sleep(0.5)  # Simular procesamiento
    return {
        'cargos_creados': 3,
        'tiempo_ejecucion': '0.5s',
        'cargos': ['CF001', 'CF002', 'CF003']
    }


def simular_realizar_desembolso(desembolso_id: int) -> Dict[str, Any]:
    """Simula la lógica de realizar desembolso"""
    print(f"    💰 Realizando desembolso {desembolso_id}...")
    time.sleep(0.8)  # Simular procesamiento
    return {
        'desembolso_realizado': True,
        'numero_transaccion': f'TXN-{desembolso_id}-{int(time.time())}',
        'tiempo_ejecucion': '0.8s'
    }


def simular_fraccionar(desembolso_id: int) -> Dict[str, Any]:
    """Simula la lógica de fraccionar"""
    print(f"    🔄 Fraccionando desembolso {desembolso_id}...")
    time.sleep(0.6)  # Simular procesamiento
    return {
        'fracciones_creadas': 2,
        'tiempo_ejecucion': '0.6s'
    }


def simular_seleccionar_pago(desembolso_id: int) -> Dict[str, Any]:
    """Simula la lógica de seleccionar pago"""
    print(f"    💳 Seleccionando método de pago para {desembolso_id}...")
    time.sleep(0.4)  # Simular procesamiento
    return {
        'metodo_pago': 'TRANSFERENCIA',
        'tiempo_ejecucion': '0.4s'
    }


def simular_autorizar(desembolso_id: int) -> Dict[str, Any]:
    """Simula la lógica de autorizar"""
    print(f"    ✅ Autorizando desembolso {desembolso_id}...")
    time.sleep(0.7)  # Simular procesamiento
    return {
        'autorizado': True,
        'codigo_autorizacion': f'AUTH-{desembolso_id}',
        'tiempo_ejecucion': '0.7s'
    }


def ejecutar_etapa_segun_nombre(desembolso_id: int, etapa_nombre: str) -> Dict[str, Any]:
    """Ejecuta la lógica correspondiente según el nombre de la etapa"""
    if 'Cargos Fijos' in etapa_nombre or 'cargos' in etapa_nombre.lower():
        return simular_grabar_cargos_fijos(desembolso_id)
    elif 'Desembolso' in etapa_nombre and 'Grabar' not in etapa_nombre:
        return simular_realizar_desembolso(desembolso_id)
    elif 'Fraccionar' in etapa_nombre:
        return simular_fraccionar(desembolso_id)
    elif 'Pago' in etapa_nombre or 'pago' in etapa_nombre.lower():
        return simular_seleccionar_pago(desembolso_id)
    elif 'Autorizar' in etapa_nombre or 'autorizar' in etapa_nombre.lower():
        return simular_autorizar(desembolso_id)
    else:
        # Etapa genérica
        print(f"    ⚙️  Ejecutando etapa genérica: {etapa_nombre}")
        time.sleep(0.3)
        return {'etapa': etapa_nombre, 'completada': True}


# ============================================================================
# CASO 1: PROCESO EXITOSO COMPLETO
# ============================================================================

def caso_1_proceso_exitoso_completo():
    """
    Caso 1: Proceso exitoso completo
    Muestra el flujo normal sin errores, procesando todas las etapas exitosamente.
    """
    print("\n" + "="*80)
    print("CASO 1: PROCESO EXITOSO COMPLETO")
    print("="*80)
    
    client = TrackingDesembolsoClient()
    
    # Paso 1: Crear ejecución con plan
    print("\n📋 Paso 1: Creando ejecución con plan completo...")
    desembolso_ids = [1, 2, 3]  # IDs de desembolsos existentes
    
    ejecucion = client.crear_ejecucion_con_plan(
        desembolso_ids=desembolso_ids,
        descripcion="Caso 1: Proceso exitoso completo - 3 desembolsos"
    )
    ejecucion_id = ejecucion['id']
    print(f"✅ Ejecución creada: ID {ejecucion_id}")
    print(f"   Total registros: {ejecucion['total_registros']}")
    print(f"   Estado: {ejecucion['estado']}")
    
    # Paso 2: Obtener procesos pendientes
    print("\n📊 Paso 2: Obteniendo procesos pendientes...")
    procesos = client.obtener_procesos_pendientes(ejecucion_id)
    print(f"✅ Procesos pendientes: {len(procesos)}")
    
    # Paso 3: Procesar cada desembolso
    print("\n🔄 Paso 3: Procesando cada desembolso...")
    
    for proceso in procesos:
        proceso_id = proceso['id']
        desembolso_id = proceso['desembolso']
        desembolso_ref = proceso.get('desembolso_referencia', f'ID-{desembolso_id}')
        
        print(f"\n  📦 Procesando desembolso: {desembolso_ref} (Proceso ID: {proceso_id})")
        
        # Procesar todas las etapas
        etapa = client.obtener_siguiente_etapa(proceso_id)
        etapa_numero = 1
        
        while etapa:
            etapa_id = etapa['id']
            etapa_nombre = etapa['etapa_nombre']
            etapa_orden = etapa['orden']
            
            print(f"\n    Etapa {etapa_numero} (Orden {etapa_orden}): {etapa_nombre}")
            
            # Iniciar etapa
            client.iniciar_etapa(etapa_id)
            print(f"    ▶️  Etapa iniciada")
            
            try:
                # Ejecutar lógica de la etapa
                resultado = ejecutar_etapa_segun_nombre(desembolso_id, etapa_nombre)
                
                # Completar etapa
                client.completar_etapa(etapa_id, datos_etapa=resultado)
                print(f"    ✅ Etapa completada exitosamente")
                
            except Exception as e:
                # Marcar error
                client.marcar_error_etapa(
                    etapa_id,
                    mensaje_error=str(e),
                    datos_etapa={'error': str(e)}
                )
                print(f"    ❌ Error en etapa: {e}")
                break  # Salir del loop de etapas
            
            # Obtener siguiente etapa
            etapa = client.obtener_siguiente_etapa(proceso_id)
            etapa_numero += 1
        
        print(f"  ✅ Proceso {proceso_id} completado exitosamente")
    
    # Paso 4: Verificar progreso
    print("\n📈 Paso 4: Verificando progreso final...")
    progreso = client.obtener_progreso(ejecucion_id)
    print(f"   Progreso: {progreso['progreso_porcentaje']}%")
    print(f"   Procesados: {progreso['registros_procesados']}/{progreso['total_registros']}")
    print(f"   Exitosos: {progreso['registros_exitosos']}")
    print(f"   Fallidos: {progreso['registros_fallidos']}")
    
    # Paso 5: Completar ejecución
    print("\n🏁 Paso 5: Completando ejecución...")
    ejecucion_completada = client.completar_ejecucion(ejecucion_id)
    print(f"✅ Ejecución {ejecucion_id} completada exitosamente")
    print(f"   Estado final: {ejecucion_completada['estado']}")
    
    print("\n" + "="*80)
    print("✅ CASO 1 COMPLETADO EXITOSAMENTE")
    print("="*80 + "\n")


# ============================================================================
# CASO 2: PROCESO CON ERROR Y REINTENTO
# ============================================================================

def caso_2_proceso_con_error_y_reintento():
    """
    Caso 2: Proceso con error y reintento
    Muestra cómo manejar errores en una etapa y reintentar el proceso.
    """
    print("\n" + "="*80)
    print("CASO 2: PROCESO CON ERROR Y REINTENTO")
    print("="*80)
    
    client = TrackingDesembolsoClient()
    
    # Paso 1: Crear ejecución con plan
    print("\n📋 Paso 1: Creando ejecución con plan completo...")
    desembolso_ids = [4, 5]  # IDs de desembolsos existentes
    
    ejecucion = client.crear_ejecucion_con_plan(
        desembolso_ids=desembolso_ids,
        descripcion="Caso 2: Proceso con error y reintento - 2 desembolsos"
    )
    ejecucion_id = ejecucion['id']
    print(f"✅ Ejecución creada: ID {ejecucion_id}")
    
    # Paso 2: Obtener procesos pendientes
    procesos = client.obtener_procesos_pendientes(ejecucion_id)
    print(f"✅ Procesos pendientes: {len(procesos)}")
    
    # Paso 3: Procesar con error simulado
    print("\n🔄 Paso 3: Procesando con error simulado...")
    
    proceso = procesos[0]
    proceso_id = proceso['id']
    desembolso_id = proceso['desembolso']
    desembolso_ref = proceso.get('desembolso_referencia', f'ID-{desembolso_id}')
    
    print(f"\n  📦 Procesando desembolso: {desembolso_ref} (Proceso ID: {proceso_id})")
    
    # Obtener primera etapa
    etapa = client.obtener_siguiente_etapa(proceso_id)
    
    if etapa:
        etapa_id = etapa['id']
        etapa_nombre = etapa['etapa_nombre']
        
        print(f"\n    Etapa: {etapa_nombre}")
        
        # Iniciar etapa
        client.iniciar_etapa(etapa_id)
        print(f"    ▶️  Etapa iniciada")
        
        # Simular error
        print(f"    ⚠️  Simulando error en la etapa...")
        error_msg = "Error de conexión con servicio externo"
        client.marcar_error_etapa(
            etapa_id,
            mensaje_error=error_msg,
            datos_etapa={
                'error_code': 'CONNECTION_TIMEOUT',
                'intento': 1
            }
        )
        print(f"    ❌ Error registrado: {error_msg}")
    
    # Paso 4: Reintentar etapa
    print("\n🔄 Paso 4: Reintentando etapa con error...")
    
    # Obtener proceso actualizado para encontrar etapa con error
    response = client.session.get(f'{client.base_url}/procesos-desembolso/{proceso_id}/')
    proceso_actualizado = response.json()
    etapas = proceso_actualizado.get('etapas', [])
    
    etapa_error = next((e for e in etapas if e['estado'] == 'ERROR'), None)
    
    if etapa_error:
        etapa_error_id = etapa_error['id']
        print(f"    🔄 Reintentando etapa: {etapa_error['etapa_nombre']}")
        
        # Reintentar
        etapa_reintentada = client.reintentar_etapa(etapa_error_id)
        print(f"    ✅ Etapa reintentada (intentos: {etapa_reintentada['intentos']})")
        
        # Ahora procesar correctamente
        print(f"    ▶️  Procesando etapa correctamente...")
        resultado = ejecutar_etapa_segun_nombre(desembolso_id, etapa_error['etapa_nombre'])
        
        # Completar etapa
        client.completar_etapa(etapa_error_id, datos_etapa=resultado)
        print(f"    ✅ Etapa completada exitosamente después del reintento")
    
    # Continuar con las demás etapas
    print("\n🔄 Continuando con las etapas restantes...")
    etapa = client.obtener_siguiente_etapa(proceso_id)
    
    while etapa:
        etapa_id = etapa['id']
        etapa_nombre = etapa['etapa_nombre']
        
        print(f"\n    Etapa: {etapa_nombre}")
        
        # Iniciar etapa
        client.iniciar_etapa(etapa_id)
        print(f"    ▶️  Etapa iniciada")
        
        # Ejecutar lógica
        resultado = ejecutar_etapa_segun_nombre(desembolso_id, etapa_nombre)
        
        # Completar etapa
        client.completar_etapa(etapa_id, datos_etapa=resultado)
        print(f"    ✅ Etapa completada")
        
        # Siguiente etapa
        etapa = client.obtener_siguiente_etapa(proceso_id)
    
    print(f"\n  ✅ Proceso {proceso_id} completado después del reintento")
    
    # Verificar progreso
    progreso = client.obtener_progreso(ejecucion_id)
    print(f"\n📈 Progreso final: {progreso['progreso_porcentaje']}%")
    
    print("\n" + "="*80)
    print("✅ CASO 2 COMPLETADO EXITOSAMENTE")
    print("="*80 + "\n")


# ============================================================================
# CASO 3: RETOMAR EJECUCIÓN FALLIDA
# ============================================================================

def caso_3_retomar_ejecucion_fallida():
    """
    Caso 3: Retomar ejecución fallida
    Muestra cómo retomar una ejecución que falló previamente, continuando
    desde donde quedó.
    """
    print("\n" + "="*80)
    print("CASO 3: RETOMAR EJECUCIÓN FALLIDA")
    print("="*80)
    
    client = TrackingDesembolsoClient()
    
    # Paso 1: Crear ejecución y simular fallo parcial
    print("\n📋 Paso 1: Creando ejecución y simulando fallo parcial...")
    desembolso_ids = [6, 7, 8]  # IDs de desembolsos existentes
    
    ejecucion = client.crear_ejecucion_con_plan(
        desembolso_ids=desembolso_ids,
        descripcion="Caso 3: Ejecución que fallará parcialmente"
    )
    ejecucion_id = ejecucion['id']
    print(f"✅ Ejecución creada: ID {ejecucion_id}")
    
    # Procesar parcialmente y luego simular fallo
    procesos = client.obtener_procesos_pendientes(ejecucion_id)
    
    # Procesar el primer proceso completamente
    if procesos:
        proceso1 = procesos[0]
        proceso1_id = proceso1['id']
        desembolso1_id = proceso1['desembolso']
        
        print(f"\n  📦 Procesando desembolso 1 completamente...")
        etapa = client.obtener_siguiente_etapa(proceso1_id)
        
        while etapa:
            etapa_id = etapa['id']
            etapa_nombre = etapa['etapa_nombre']
            
            client.iniciar_etapa(etapa_id)
            resultado = ejecutar_etapa_segun_nombre(desembolso1_id, etapa_nombre)
            client.completar_etapa(etapa_id, datos_etapa=resultado)
            
            etapa = client.obtener_siguiente_etapa(proceso1_id)
        
        print(f"  ✅ Proceso 1 completado")
    
    # Procesar parcialmente el segundo proceso y luego fallar
    if len(procesos) > 1:
        proceso2 = procesos[1]
        proceso2_id = proceso2['id']
        desembolso2_id = proceso2['desembolso']
        
        print(f"\n  📦 Procesando desembolso 2 parcialmente (simulando fallo)...")
        etapa = client.obtener_siguiente_etapa(proceso2_id)
        
        if etapa:
            etapa_id = etapa['id']
            etapa_nombre = etapa['etapa_nombre']
            
            client.iniciar_etapa(etapa_id)
            # Simular fallo
            client.marcar_error_etapa(
                etapa_id,
                mensaje_error="Error simulado para demostrar retomado",
                datos_etapa={'simulado': True}
            )
            print(f"  ❌ Proceso 2 falló en etapa: {etapa_nombre}")
    
    # Marcar ejecución como fallida
    print("\n⚠️  Marcando ejecución como fallida...")
    response = client.session.post(
        f'{client.base_url}/ejecuciones/{ejecucion_id}/fallar/',
        json={'mensaje_error': 'Fallo parcial simulado para demostración'}
    )
    response.raise_for_status()
    print(f"✅ Ejecución marcada como fallida")
    
    # Paso 2: Retomar ejecución
    print("\n🔄 Paso 2: Retomando ejecución fallida...")
    
    # Obtener ejecuciones pendientes
    response = client.session.get(
        f'{client.base_url}/ejecuciones/pendientes/',
        params={'tipo_proceso': 'DESEMBOLSO'}
    )
    ejecuciones_pendientes = response.json()
    
    ejecucion_retomar = next(
        (e for e in ejecuciones_pendientes if e['id'] == ejecucion_id),
        None
    )
    
    if ejecucion_retomar:
        print(f"   Ejecución encontrada: ID {ejecucion_id}")
        print(f"   Estado actual: {ejecucion_retomar['estado']}")
        
        # Retomar ejecución
        response = client.session.post(
            f'{client.base_url}/ejecuciones/{ejecucion_id}/retomar/'
        )
        response.raise_for_status()
        ejecucion_retomada = response.json()
        print(f"✅ Ejecución retomada. Nuevo estado: {ejecucion_retomada['estado']}")
    
    # Paso 3: Continuar procesando desde donde quedó
    print("\n🔄 Paso 3: Continuando procesamiento desde donde quedó...")
    
    # Obtener procesos pendientes o con error
    response = client.session.get(
        f'{client.base_url}/procesos-desembolso/',
        params={'ejecucion': ejecucion_id}
    )
    procesos_actualizados = response.json().get('results', [])
    
    for proceso in procesos_actualizados:
        proceso_id = proceso['id']
        estado = proceso['estado_general']
        desembolso_id = proceso['desembolso']
        desembolso_ref = proceso.get('desembolso_referencia', f'ID-{desembolso_id}')
        
        print(f"\n  📦 Proceso: {desembolso_ref} - Estado: {estado}")
        
        if estado == 'COMPLETADO':
            print(f"    ✅ Ya está completado, saltando...")
            continue
        
        # Si tiene error, obtener etapa con error
        if estado == 'ERROR':
            etapas = proceso.get('etapas', [])
            etapa_error = next((e for e in etapas if e['estado'] == 'ERROR'), None)
            
            if etapa_error:
                print(f"    🔄 Reintentando etapa con error: {etapa_error['etapa_nombre']}")
                etapa_reintentada = client.reintentar_etapa(etapa_error['id'])
                print(f"    ✅ Etapa reintentada")
        
        # Continuar procesando
        etapa = client.obtener_siguiente_etapa(proceso_id)
        
        while etapa:
            etapa_id = etapa['id']
            etapa_nombre = etapa['etapa_nombre']
            
            print(f"    ▶️  Procesando etapa: {etapa_nombre}")
            
            client.iniciar_etapa(etapa_id)
            resultado = ejecutar_etapa_segun_nombre(desembolso_id, etapa_nombre)
            client.completar_etapa(etapa_id, datos_etapa=resultado)
            
            print(f"    ✅ Etapa completada")
            
            etapa = client.obtener_siguiente_etapa(proceso_id)
        
        print(f"  ✅ Proceso {proceso_id} completado")
    
    # Paso 4: Verificar progreso final
    print("\n📈 Paso 4: Verificando progreso final...")
    progreso = client.obtener_progreso(ejecucion_id)
    print(f"   Progreso: {progreso['progreso_porcentaje']}%")
    print(f"   Procesados: {progreso['registros_procesados']}/{progreso['total_registros']}")
    print(f"   Exitosos: {progreso['registros_exitosos']}")
    print(f"   Fallidos: {progreso['registros_fallidos']}")
    
    # Completar ejecución
    if progreso['registros_procesados'] == progreso['total_registros']:
        print("\n🏁 Completando ejecución...")
        client.completar_ejecucion(ejecucion_id)
        print(f"✅ Ejecución {ejecucion_id} completada exitosamente")
    
    print("\n" + "="*80)
    print("✅ CASO 3 COMPLETADO EXITOSAMENTE")
    print("="*80 + "\n")


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Ejecuta todos los casos de uso"""
    print("\n" + "="*80)
    print("EJEMPLOS DE TRACKING PARA DESEMBOLSOS")
    print("="*80)
    print("\nEste script demuestra 3 casos de uso completos del sistema de tracking:")
    print("1. Proceso exitoso completo")
    print("2. Proceso con error y reintento")
    print("3. Retomar ejecución fallida")
    print("\n⚠️  NOTA: Asegúrate de que:")
    print("   - El servidor Django esté corriendo en http://localhost:8000")
    print("   - Existan desembolsos con IDs 1-8 en la base de datos")
    print("   - Los desembolsos tengan un tipo_desembolso asignado")
    print("   - El tipo_desembolso tenga etapas configuradas")
    print("\n" + "="*80)
    
    try:
        # Ejecutar casos
        caso_1_proceso_exitoso_completo()
        caso_2_proceso_con_error_y_reintento()
        caso_3_retomar_ejecucion_fallida()
        
        print("\n" + "="*80)
        print("✅ TODOS LOS CASOS COMPLETADOS EXITOSAMENTE")
        print("="*80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor.")
        print("   Asegúrate de que el servidor Django esté corriendo:")
        print("   python manage.py runserver")
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ ERROR HTTP: {e}")
        print(f"   Respuesta: {e.response.text}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

