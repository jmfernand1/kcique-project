"""
Cliente completo para procesar DataFrames y enviar datos a la API de Dexter.

Este cliente procesa DataFrames donde la información de desembolso y garantía
se repite según los cargos fijos que tenga, construye los JSONs necesarios
y los envía a la API.
"""

import pandas as pd
import requests
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json
from .dataframe_client import DataFrameAPIClient


class DataFrameAPIClientCompleto(DataFrameAPIClient):
    """
    Cliente completo que procesa DataFrames y envía datos a la API.
    
    Extiende DataFrameAPIClient agregando funcionalidad para enviar
    los datos construidos a la API REST de Dexter.
    """
    
    def __init__(self,
                 base_url: str = "http://localhost:8000/dexter/api",
                 desembolso_key: str = 'referencia',
                 garantia_key: Optional[str] = None,
                 session: Optional[requests.Session] = None):
        """
        Inicializa el cliente completo.
        
        Args:
            base_url: URL base de la API
            desembolso_key: Nombre de la columna que identifica únicamente un desembolso
            garantia_key: Nombre de la columna que identifica únicamente una garantía
            session: Sesión de requests (opcional, para mantener cookies/auth)
        """
        super().__init__(desembolso_key, garantia_key)
        self.base_url = base_url.rstrip('/')
        self.session = session or requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def procesar_y_enviar(self,
                          df: pd.DataFrame,
                          crear_garantias: bool = True,
                          actualizar_existentes: bool = False) -> Dict[str, Any]:
        """
        Procesa el DataFrame y envía todos los datos a la API.
        
        Args:
            df: DataFrame con información de desembolsos, garantías y cargos fijos
            crear_garantias: Si True, crea/actualiza garantías también
            actualizar_existentes: Si True, actualiza desembolsos/garantías existentes
                                  Si False, solo crea nuevos
        
        Returns:
            Dict con el resultado del procesamiento:
            - 'desembolsos_creados': Lista de IDs de desembolsos creados
            - 'desembolsos_actualizados': Lista de IDs de desembolsos actualizados
            - 'cargos_fijos_creados': Lista de IDs de cargos fijos creados
            - 'garantias_creadas': Lista de IDs de garantías creadas
            - 'garantias_actualizadas': Lista de IDs de garantías actualizadas
            - 'errores': Lista de errores encontrados
        """
        # Validar DataFrame
        validacion = self.validar_dataframe(df)
        if not validacion['valido']:
            return {
                'exito': False,
                'errores': validacion['errores'],
                'desembolsos_creados': [],
                'desembolsos_actualizados': [],
                'cargos_fijos_creados': [],
                'garantias_creadas': [],
                'garantias_actualizadas': [],
            }
        
        # Procesar DataFrame
        datos = self.procesar_dataframe(df)
        
        resultado = {
            'exito': True,
            'desembolsos_creados': [],
            'desembolsos_actualizados': [],
            'cargos_fijos_creados': [],
            'garantias_creadas': [],
            'garantias_actualizadas': [],
            'errores': []
        }
        
        # Mapeo de referencias a IDs de desembolsos creados
        referencia_a_id = {}
        
        # 1. Crear/actualizar desembolsos
        for desembolso_data in datos['desembolsos']:
            referencia = desembolso_data.get('referencia')
            if not referencia:
                resultado['errores'].append("Desembolso sin referencia")
                continue
            
            try:
                # Verificar si existe
                desembolso_existente = self._buscar_desembolso_por_referencia(referencia)
                
                if desembolso_existente and actualizar_existentes:
                    # Actualizar desembolso existente
                    desembolso_id = desembolso_existente['id']
                    response = self.session.patch(
                        f"{self.base_url}/desembolsos/{desembolso_id}/",
                        json=desembolso_data
                    )
                    response.raise_for_status()
                    referencia_a_id[referencia] = desembolso_id
                    resultado['desembolsos_actualizados'].append(desembolso_id)
                elif not desembolso_existente:
                    # Crear nuevo desembolso
                    response = self.session.post(
                        f"{self.base_url}/desembolsos/",
                        json=desembolso_data
                    )
                    response.raise_for_status()
                    desembolso_creado = response.json()
                    desembolso_id = desembolso_creado['id']
                    referencia_a_id[referencia] = desembolso_id
                    resultado['desembolsos_creados'].append(desembolso_id)
                else:
                    # Ya existe y no se actualiza
                    referencia_a_id[referencia] = desembolso_existente['id']
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Error al procesar desembolso {referencia}: {str(e)}"
                resultado['errores'].append(error_msg)
                continue
        
        # 2. Crear cargos fijos
        for cargo_data in datos['cargos_fijos']:
            referencia = cargo_data.pop('referencia_desembolso', None)
            if not referencia or referencia not in referencia_a_id:
                resultado['errores'].append(f"Cargo fijo sin desembolso válido: {cargo_data.get('codigo', 'N/A')}")
                continue
            
            desembolso_id = referencia_a_id[referencia]
            cargo_data['desembolso'] = desembolso_id
            
            try:
                response = self.session.post(
                    f"{self.base_url}/cargos-fijos/",
                    json=cargo_data
                )
                response.raise_for_status()
                cargo_creado = response.json()
                resultado['cargos_fijos_creados'].append(cargo_creado['id'])
            except requests.exceptions.RequestException as e:
                error_msg = f"Error al crear cargo fijo {cargo_data.get('codigo', 'N/A')}: {str(e)}"
                resultado['errores'].append(error_msg)
        
        # 3. Crear/actualizar garantías (si se solicita)
        if crear_garantias and datos['garantias']:
            for garantia_data in datos['garantias']:
                placa = garantia_data.get('placa')
                referencia_gar = garantia_data.get('referencia')
                
                if not placa and not referencia_gar:
                    resultado['errores'].append("Garantía sin placa ni referencia")
                    continue
                
                try:
                    # Buscar garantía existente por placa o referencia
                    garantia_existente = None
                    if placa:
                        garantia_existente = self._buscar_garantia_por_placa(placa)
                    elif referencia_gar:
                        garantia_existente = self._buscar_garantia_por_referencia(referencia_gar)
                    
                    if garantia_existente and actualizar_existentes:
                        # Actualizar garantía existente
                        garantia_id = garantia_existente['id']
                        response = self.session.patch(
                            f"{self.base_url}/garantias/{garantia_id}/",
                            json=garantia_data
                        )
                        response.raise_for_status()
                        resultado['garantias_actualizadas'].append(garantia_id)
                    elif not garantia_existente:
                        # Crear nueva garantía
                        response = self.session.post(
                            f"{self.base_url}/garantias/",
                            json=garantia_data
                        )
                        response.raise_for_status()
                        garantia_creada = response.json()
                        resultado['garantias_creadas'].append(garantia_creada['id'])
                    
                except requests.exceptions.RequestException as e:
                    error_msg = f"Error al procesar garantía {placa or referencia_gar}: {str(e)}"
                    resultado['errores'].append(error_msg)
        
        return resultado
    
    def _buscar_desembolso_por_referencia(self, referencia: str) -> Optional[Dict]:
        """Busca un desembolso por su referencia."""
        try:
            response = self.session.get(
                f"{self.base_url}/desembolsos/",
                params={'referencia': referencia}
            )
            response.raise_for_status()
            resultados = response.json()
            
            # Si es paginado, buscar en results
            if 'results' in resultados:
                for desembolso in resultados['results']:
                    if desembolso.get('referencia') == referencia:
                        return desembolso
            elif isinstance(resultados, list):
                for desembolso in resultados:
                    if desembolso.get('referencia') == referencia:
                        return desembolso
            elif isinstance(resultados, dict) and resultados.get('referencia') == referencia:
                return resultados
            
            return None
        except requests.exceptions.RequestException:
            return None
    
    def _buscar_garantia_por_placa(self, placa: str) -> Optional[Dict]:
        """Busca una garantía por su placa."""
        try:
            response = self.session.get(
                f"{self.base_url}/garantias/",
                params={'placa': placa}
            )
            response.raise_for_status()
            resultados = response.json()
            
            if 'results' in resultados:
                for garantia in resultados['results']:
                    if garantia.get('placa') == placa:
                        return garantia
            elif isinstance(resultados, list):
                for garantia in resultados:
                    if garantia.get('placa') == placa:
                        return garantia
            elif isinstance(resultados, dict) and resultados.get('placa') == placa:
                return resultados
            
            return None
        except requests.exceptions.RequestException:
            return None
    
    def _buscar_garantia_por_referencia(self, referencia: str) -> Optional[Dict]:
        """Busca una garantía por su referencia."""
        try:
            response = self.session.get(
                f"{self.base_url}/garantias/",
                params={'referencia': referencia}
            )
            response.raise_for_status()
            resultados = response.json()
            
            if 'results' in resultados:
                for garantia in resultados['results']:
                    if garantia.get('referencia') == referencia:
                        return garantia
            elif isinstance(resultados, list):
                for garantia in resultados:
                    if garantia.get('referencia') == referencia:
                        return garantia
            elif isinstance(resultados, dict) and resultados.get('referencia') == referencia:
                return resultados
            
            return None
        except requests.exceptions.RequestException:
            return None
    
    def procesar_solo_json(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Procesa el DataFrame y retorna solo los JSONs sin enviar a la API.
        
        Útil para revisar los datos antes de enviarlos.
        
        Args:
            df: DataFrame con información
            
        Returns:
            Dict con los JSONs listos para enviar
        """
        return self.procesar_dataframe(df)
    
    def enviar_jsons(self,
                    datos: Dict[str, List[Dict]],
                    crear_garantias: bool = True,
                    actualizar_existentes: bool = False) -> Dict[str, Any]:
        """
        Envía JSONs previamente construidos a la API.
        
        Args:
            datos: Dict con 'desembolsos', 'cargos_fijos', 'garantias'
            crear_garantias: Si True, crea/actualiza garantías también
            actualizar_existentes: Si True, actualiza existentes
        
        Returns:
            Dict con el resultado del envío
        """
        # Convertir datos a DataFrame temporal para usar procesar_y_enviar
        # Esto es un workaround, pero funciona
        resultado = {
            'exito': True,
            'desembolsos_creados': [],
            'desembolsos_actualizados': [],
            'cargos_fijos_creados': [],
            'garantias_creadas': [],
            'garantias_actualizadas': [],
            'errores': []
        }
        
        referencia_a_id = {}
        
        # Procesar desembolsos
        for desembolso_data in datos.get('desembolsos', []):
            referencia = desembolso_data.get('referencia')
            if not referencia:
                resultado['errores'].append("Desembolso sin referencia")
                continue
            
            try:
                desembolso_existente = self._buscar_desembolso_por_referencia(referencia)
                
                if desembolso_existente and actualizar_existentes:
                    desembolso_id = desembolso_existente['id']
                    response = self.session.patch(
                        f"{self.base_url}/desembolsos/{desembolso_id}/",
                        json=desembolso_data
                    )
                    response.raise_for_status()
                    referencia_a_id[referencia] = desembolso_id
                    resultado['desembolsos_actualizados'].append(desembolso_id)
                elif not desembolso_existente:
                    response = self.session.post(
                        f"{self.base_url}/desembolsos/",
                        json=desembolso_data
                    )
                    response.raise_for_status()
                    desembolso_creado = response.json()
                    desembolso_id = desembolso_creado['id']
                    referencia_a_id[referencia] = desembolso_id
                    resultado['desembolsos_creados'].append(desembolso_id)
                else:
                    referencia_a_id[referencia] = desembolso_existente['id']
                    
            except requests.exceptions.RequestException as e:
                error_msg = f"Error al procesar desembolso {referencia}: {str(e)}"
                resultado['errores'].append(error_msg)
        
        # Procesar cargos fijos
        for cargo_data in datos.get('cargos_fijos', []):
            referencia = cargo_data.pop('referencia_desembolso', None)
            if not referencia or referencia not in referencia_a_id:
                resultado['errores'].append(f"Cargo fijo sin desembolso válido")
                continue
            
            desembolso_id = referencia_a_id[referencia]
            cargo_data['desembolso'] = desembolso_id
            
            try:
                response = self.session.post(
                    f"{self.base_url}/cargos-fijos/",
                    json=cargo_data
                )
                response.raise_for_status()
                cargo_creado = response.json()
                resultado['cargos_fijos_creados'].append(cargo_creado['id'])
            except requests.exceptions.RequestException as e:
                error_msg = f"Error al crear cargo fijo: {str(e)}"
                resultado['errores'].append(error_msg)
        
        # Procesar garantías
        if crear_garantias:
            for garantia_data in datos.get('garantias', []):
                placa = garantia_data.get('placa')
                referencia_gar = garantia_data.get('referencia')
                
                if not placa and not referencia_gar:
                    resultado['errores'].append("Garantía sin placa ni referencia")
                    continue
                
                try:
                    garantia_existente = None
                    if placa:
                        garantia_existente = self._buscar_garantia_por_placa(placa)
                    elif referencia_gar:
                        garantia_existente = self._buscar_garantia_por_referencia(referencia_gar)
                    
                    if garantia_existente and actualizar_existentes:
                        garantia_id = garantia_existente['id']
                        response = self.session.patch(
                            f"{self.base_url}/garantias/{garantia_id}/",
                            json=garantia_data
                        )
                        response.raise_for_status()
                        resultado['garantias_actualizadas'].append(garantia_id)
                    elif not garantia_existente:
                        response = self.session.post(
                            f"{self.base_url}/garantias/",
                            json=garantia_data
                        )
                        response.raise_for_status()
                        garantia_creada = response.json()
                        resultado['garantias_creadas'].append(garantia_creada['id'])
                    
                except requests.exceptions.RequestException as e:
                    error_msg = f"Error al procesar garantía: {str(e)}"
                    resultado['errores'].append(error_msg)
        
        return resultado


def ejemplo_uso_completo():
    """Ejemplo de uso del cliente completo."""
    import pandas as pd
    
    # Crear un DataFrame de ejemplo
    data = {
        'referencia': ['DES-001', 'DES-001', 'DES-001', 'DES-002', 'DES-002'],
        'obligacion': [123456, 123456, 123456, 789012, 789012],
        'id_cliente': [100, 100, 100, 200, 200],
        'nit_beneficiario': [900123456, 900123456, 900123456, 900789012, 900789012],
        'aliado': ['ALIADO1', 'ALIADO1', 'ALIADO1', 'ALIADO2', 'ALIADO2'],
        'tipo_cta_destino': ['Ahorros', 'Ahorros', 'Ahorros', 'Corriente', 'Corriente'],
        'cod_tipo_cuenta_destino': [1, 1, 1, 2, 2],
        'num_cta_destino': [1234567890, 1234567890, 1234567890, 9876543210, 9876543210],
        'banco_destino': ['Banco1', 'Banco1', 'Banco1', 'Banco2', 'Banco2'],
        'cod_banco_destino': [51, 51, 51, 52, 52],
        'valor_desembolso': [1000000, 1000000, 1000000, 2000000, 2000000],
        'numero_tramos': [1, 1, 1, 2, 2],
        'plazo_tramo_1': [12, 12, 12, 24, 24],
        'tipo_tasa_tramo_1': ['EA', 'EA', 'EA', 'EA', 'EA'],
        'tasa_tramo_1': [15.5, 15.5, 15.5, 16.0, 16.0],
        'amortizacion_tramo_1': ['FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA'],
        'plazo_tramo_2': [0, 0, 0, 12, 12],
        'tipo_tasa_tramo_2': ['EA', 'EA', 'EA', 'EA', 'EA'],
        'tasa_tramo_2': [0.0, 0.0, 0.0, 14.0, 14.0],
        'amortizacion_tramo_2': ['FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA'],
        'codigo': ['CF001', 'CF002', 'CF003', 'CF001', 'CF002'],
        'nombre_cargo_fijo': ['Admin', 'Seguro', 'Mantenimiento', 'Admin', 'Seguro'],
        'valor': [50000, 100000, 200000, 60000, 120000],
        'periodicidad': ['MENSUAL', 'TRIMESTRAL', 'ANUAL', 'MENSUAL', 'TRIMESTRAL'],
        'fecha_efectiva': ['2025-01-01', '2025-01-01', '2025-01-01', '2025-01-01', '2025-01-01'],
        'placa': ['ABC123', 'ABC123', 'ABC123', 'XYZ789', 'XYZ789'],
        'cod_fasecolda': ['F001', 'F001', 'F001', 'F002', 'F002'],
        'codigo_fasecolda': ['F001', 'F001', 'F001', 'F002', 'F002'],
        'id_garante': [500, 500, 500, 600, 600]
    }
    
    df = pd.DataFrame(data)
    
    # Crear cliente
    client = DataFrameAPIClientCompleto(
        base_url="http://localhost:8000/dexter/api",
        desembolso_key='referencia',
        garantia_key='placa'
    )
    
    # Opción 1: Solo generar JSONs sin enviar
    print("=== Generando JSONs ===")
    datos = client.procesar_solo_json(df)
    print(f"Desembolsos: {len(datos['desembolsos'])}")
    print(f"Cargos fijos: {len(datos['cargos_fijos'])}")
    print(f"Garantías: {len(datos['garantias'])}")
    
    # Opción 2: Procesar y enviar directamente
    # print("\n=== Enviando a la API ===")
    # resultado = client.procesar_y_enviar(df, crear_garantias=True, actualizar_existentes=False)
    # print(f"Desembolsos creados: {len(resultado['desembolsos_creados'])}")
    # print(f"Cargos fijos creados: {len(resultado['cargos_fijos_creados'])}")
    # print(f"Garantías creadas: {len(resultado['garantias_creadas'])}")
    # if resultado['errores']:
    #     print(f"Errores: {resultado['errores']}")


if __name__ == '__main__':
    ejemplo_uso_completo()

