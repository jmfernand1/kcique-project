"""
Cliente para procesar DataFrames y construir JSONs para la API de Dexter.

Este cliente procesa DataFrames donde la información de desembolso y garantía
se repite según los cargos fijos que tenga, y construye los JSONs necesarios
para enviar la información a los modelos de datos vía API.
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class DataFrameAPIClient:
    """
    Cliente para procesar DataFrames y construir JSONs para la API.
    
    El DataFrame debe tener columnas que incluyan:
    - Información de desembolso (se repite por cada cargo fijo)
    - Información de garantía (se repite por cada cargo fijo, opcional)
    - Información de cargos fijos (una fila por cada cargo fijo)
    """
    
    # Campos del modelo Desembolso
    DESEMBOLSO_FIELDS = [
        'referencia', 'obligacion', 'id_cliente', 'nit_beneficiario', 'aliado',
        'tipo_cta_destino', 'cod_tipo_cuenta_destino', 'num_cta_destino',
        'banco_destino', 'cod_banco_destino', 'valor_desembolso', 'numero_tramos',
        'plazo_tramo_1', 'tipo_tasa_tramo_1', 'tasa_tramo_1', 'amortizacion_tramo_1',
        'plazo_tramo_2', 'tipo_tasa_tramo_2', 'tasa_tramo_2', 'amortizacion_tramo_2',
        'dia_pago_cuota', 'estado', 'tipo_desembolso', 'observaciones', 'ids_sharepoint'
    ]
    
    # Campos del modelo CargoFijo
    CARGO_FIJO_FIELDS = [
        'codigo', 'nombre_cargo_fijo', 'fecha_efectiva', 'fecha_revision',
        'periodicidad', 'valor'
    ]
    
    # Campos del modelo Garantia
    GARANTIA_FIELDS = [
        'referencia', 'obligacion', 'id_cliente', 'id_garante', 'cod_fasecolda',
        'codigo_fasecolda', 'color', 'placa', 'poliza_vehiculo', 'cod_aseguradora',
        'nro_poliza', 'valor_asegurado', 'fecha_vencimiento_seguro', 'tipo_prima',
        'valor_prima', 'folio_electronico', 'valor_vehiculo', 'modelo',
        'fecha_prenda', 'chasis', 'motor', 'serie', 'servicio', 'fecha_desembolso',
        'estado'
    ]
    
    def __init__(self, 
                 desembolso_key: str = 'referencia',
                 garantia_key: Optional[str] = None):
        """
        Inicializa el cliente.
        
        Args:
            desembolso_key: Nombre de la columna que identifica únicamente un desembolso
            garantia_key: Nombre de la columna que identifica únicamente una garantía
                         (por defecto usa 'placa' si existe en el DataFrame)
        """
        self.desembolso_key = desembolso_key
        self.garantia_key = garantia_key
    
    def procesar_dataframe(self, df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        Procesa el DataFrame y construye los JSONs listos para enviar vía API.
        
        Args:
            df: DataFrame con información de desembolsos, garantías y cargos fijos
            
        Returns:
            Dict con las siguientes claves:
            - 'desembolsos': Lista de JSONs para crear/actualizar desembolsos
            - 'cargos_fijos': Lista de JSONs para crear cargos fijos
            - 'garantias': Lista de JSONs para crear/actualizar garantías (si aplica)
        """
        if df.empty:
            return {
                'desembolsos': [],
                'cargos_fijos': [],
                'garantias': []
            }
        
        # Agrupar por desembolso
        desembolsos_data = {}
        garantias_data = {}
        
        # Agrupar el DataFrame por la clave de desembolso
        for referencia, group in df.groupby(self.desembolso_key):
            # Obtener la primera fila para extraer datos únicos del desembolso
            primera_fila = group.iloc[0]
            
            # Construir JSON del desembolso
            desembolso_json = self._construir_desembolso_json(primera_fila)
            desembolsos_data[referencia] = {
                'desembolso': desembolso_json,
                'cargos_fijos': [],
                'garantia': None
            }
            
            # Extraer cargos fijos de todas las filas del grupo
            for _, row in group.iterrows():
                cargo_fijo_json = self._construir_cargo_fijo_json(row)
                if cargo_fijo_json:
                    desembolsos_data[referencia]['cargos_fijos'].append(cargo_fijo_json)
            
            # Extraer información de garantía si existe
            garantia_json = self._construir_garantia_json(primera_fila)
            if garantia_json:
                # Si hay una clave de garantía, agrupar garantías también
                garantia_id = self._obtener_garantia_key(primera_fila)
                if garantia_id:
                    garantias_data[garantia_id] = garantia_json
                    desembolsos_data[referencia]['garantia'] = garantia_id
        
        # Construir la respuesta final
        resultado = {
            'desembolsos': [data['desembolso'] for data in desembolsos_data.values()],
            'cargos_fijos': [],
            'garantias': list(garantias_data.values()) if garantias_data else []
        }
        
        # Agregar cargos fijos con referencia al desembolso
        # Nota: Los cargos fijos necesitan el ID del desembolso después de crearlo
        # Por ahora los dejamos sin el ID, se debe actualizar después de crear el desembolso
        for referencia, data in desembolsos_data.items():
            for cargo in data['cargos_fijos']:
                cargo['referencia_desembolso'] = referencia  # Para referencia temporal
                resultado['cargos_fijos'].append(cargo)
        
        return resultado
    
    def _construir_desembolso_json(self, row: pd.Series) -> Dict[str, Any]:
        """
        Construye el JSON para un desembolso desde una fila del DataFrame.
        
        Detecta automáticamente columnas de SharePoint que empiecen con:
        - id_sharepoint_*
        - sharepoint_*
        - sp_*
        
        Y las agrupa en el diccionario ids_sharepoint. Por ejemplo:
        - id_sharepoint_documento_1 -> ids_sharepoint['documento_1']
        - sharepoint_contrato -> ids_sharepoint['contrato']
        """
        desembolso = {}
        ids_sharepoint_dict = {}
        
        # Procesar campos estándar del desembolso
        for field in self.DESEMBOLSO_FIELDS:
            if field in row.index:
                value = row[field]
                # Convertir NaN a None
                if pd.isna(value):
                    value = None
                # Convertir tipos según el campo
                elif field in ['obligacion', 'id_cliente', 'nit_beneficiario', 
                              'num_cta_destino', 'cod_tipo_cuenta_destino', 
                              'cod_banco_destino', 'numero_tramos', 'plazo_tramo_1',
                              'plazo_tramo_2', 'dia_pago_cuota']:
                    value = int(value) if value is not None else None
                elif field in ['valor_desembolso', 'tasa_tramo_1', 'tasa_tramo_2']:
                    value = float(value) if value is not None else None
                elif field == 'observaciones':
                    # Intentar parsear JSON si es string
                    if isinstance(value, str):
                        try:
                            value = json.loads(value)
                        except (json.JSONDecodeError, ValueError):
                            value = {}
                    elif pd.isna(value) or value is None:
                        value = {}
                elif field == 'ids_sharepoint':
                    # Si viene como JSON string, parsearlo primero
                    if isinstance(value, str):
                        try:
                            ids_sharepoint_dict = json.loads(value)
                        except (json.JSONDecodeError, ValueError):
                            ids_sharepoint_dict = {}
                    elif isinstance(value, dict):
                        ids_sharepoint_dict = value.copy()
                    elif pd.isna(value) or value is None:
                        ids_sharepoint_dict = {}
                    # No asignar aquí, se procesará después con las columnas
                    continue
                
                desembolso[field] = value
        
        # Buscar columnas de SharePoint (patrones: id_sharepoint_*, sharepoint_*, sp_*)
        sharepoint_patterns = ['id_sharepoint_', 'sharepoint_', 'sp_']
        for col in row.index:
            # Saltar si ya es un campo estándar procesado
            if col in self.DESEMBOLSO_FIELDS or col in self.CARGO_FIJO_FIELDS or col in self.GARANTIA_FIELDS:
                continue
            
            # Verificar si la columna es de SharePoint
            es_columna_sharepoint = False
            nombre_clave = col
            
            for pattern in sharepoint_patterns:
                if col.lower().startswith(pattern.lower()):
                    es_columna_sharepoint = True
                    # Extraer el nombre de la clave (sin el prefijo)
                    nombre_clave = col[len(pattern):]
                    break
            
            if es_columna_sharepoint:
                value = row[col]
                if not pd.isna(value) and value is not None:
                    # Convertir a string si es necesario
                    ids_sharepoint_dict[nombre_clave] = str(value) if not isinstance(value, str) else value
        
        # Asignar ids_sharepoint (puede ser dict vacío si no hay datos)
        desembolso['ids_sharepoint'] = ids_sharepoint_dict if ids_sharepoint_dict else {}
        
        return desembolso
    
    def _construir_cargo_fijo_json(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Construye el JSON para un cargo fijo desde una fila del DataFrame."""
        cargo_fijo = {}
        tiene_datos = False
        
        for field in self.CARGO_FIJO_FIELDS:
            if field in row.index:
                value = row[field]
                if pd.isna(value):
                    value = None
                elif field in ['fecha_efectiva', 'fecha_revision']:
                    # Convertir fechas
                    if isinstance(value, str):
                        try:
                            # Intentar parsear diferentes formatos de fecha
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                                try:
                                    value = datetime.strptime(value, fmt).date().isoformat()
                                    break
                                except ValueError:
                                    continue
                            else:
                                value = None
                        except Exception:
                            value = None
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        value = value.date().isoformat() if hasattr(value, 'date') else str(value)
                    elif pd.isna(value):
                        value = None
                elif field == 'valor':
                    value = float(value) if value is not None else None
                
                cargo_fijo[field] = value
                if value is not None:
                    tiene_datos = True
        
        # Solo retornar si tiene al menos código o nombre
        if tiene_datos and (cargo_fijo.get('codigo') or cargo_fijo.get('nombre_cargo_fijo')):
            return cargo_fijo
        
        return None
    
    def _construir_garantia_json(self, row: pd.Series) -> Optional[Dict[str, Any]]:
        """Construye el JSON para una garantía desde una fila del DataFrame."""
        garantia = {}
        tiene_datos = False
        
        for field in self.GARANTIA_FIELDS:
            if field in row.index:
                value = row[field]
                if pd.isna(value):
                    value = None
                elif field in ['obligacion', 'id_cliente', 'id_garante', 'valor_vehiculo']:
                    value = int(value) if value is not None else None
                elif field in ['valor_asegurado', 'valor_prima']:
                    value = float(value) if value is not None else None
                elif field in ['fecha_vencimiento_seguro', 'fecha_prenda', 'fecha_desembolso']:
                    # Convertir fechas
                    if isinstance(value, str):
                        try:
                            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                                try:
                                    value = datetime.strptime(value, fmt).date().isoformat()
                                    break
                                except ValueError:
                                    continue
                            else:
                                value = None
                        except Exception:
                            value = None
                    elif isinstance(value, (datetime, pd.Timestamp)):
                        value = value.date().isoformat() if hasattr(value, 'date') else str(value)
                    elif pd.isna(value):
                        value = None
                
                garantia[field] = value
                if value is not None:
                    tiene_datos = True
        
        # Solo retornar si tiene datos mínimos (placa o referencia)
        if tiene_datos and (garantia.get('placa') or garantia.get('referencia')):
            return garantia
        
        return None
    
    def _obtener_garantia_key(self, row: pd.Series) -> Optional[str]:
        """Obtiene la clave única de garantía desde una fila."""
        if self.garantia_key and self.garantia_key in row.index:
            value = row[self.garantia_key]
            return str(value) if not pd.isna(value) else None
        elif 'placa' in row.index:
            value = row['placa']
            return str(value) if not pd.isna(value) else None
        return None
    
    def obtener_resumen(self, resultado: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Obtiene un resumen del procesamiento.
        
        Args:
            resultado: Resultado de procesar_dataframe()
            
        Returns:
            Dict con estadísticas del procesamiento
        """
        return {
            'total_desembolsos': len(resultado['desembolsos']),
            'total_cargos_fijos': len(resultado['cargos_fijos']),
            'total_garantias': len(resultado['garantias']),
            'cargos_fijos_por_desembolso': len(resultado['cargos_fijos']) / len(resultado['desembolsos']) if resultado['desembolsos'] else 0
        }
    
    def validar_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Valida que el DataFrame tenga las columnas mínimas necesarias.
        
        Args:
            df: DataFrame a validar
            
        Returns:
            Dict con 'valido' (bool) y 'errores' (lista de strings)
        """
        errores = []
        
        if df.empty:
            errores.append("El DataFrame está vacío")
            return {'valido': False, 'errores': errores}
        
        # Validar que existe la columna clave de desembolso
        if self.desembolso_key not in df.columns:
            errores.append(f"Falta la columna '{self.desembolso_key}' (clave de desembolso)")
        
        # Validar que hay al menos un campo de desembolso
        campos_desembolso_encontrados = [f for f in self.DESEMBOLSO_FIELDS if f in df.columns]
        if not campos_desembolso_encontrados:
            errores.append("No se encontraron columnas de desembolso en el DataFrame")
        
        # Validar que hay al menos un campo de cargo fijo
        campos_cargo_encontrados = [f for f in self.CARGO_FIJO_FIELDS if f in df.columns]
        if not campos_cargo_encontrados:
            errores.append("No se encontraron columnas de cargo fijo en el DataFrame")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'campos_desembolso_encontrados': campos_desembolso_encontrados,
            'campos_cargo_encontrados': campos_cargo_encontrados
        }


def ejemplo_uso():
    """Ejemplo de uso del cliente."""
    import pandas as pd
    
    # Crear un DataFrame de ejemplo
    data = {
        'referencia': ['DES-001', 'DES-001', 'DES-001', 'DES-002', 'DES-002'],
        'obligacion': [123456, 123456, 123456, 789012, 789012],
        'id_cliente': [100, 100, 100, 200, 200],
        'valor_desembolso': [1000000, 1000000, 1000000, 2000000, 2000000],
        'aliado': ['ALIADO1', 'ALIADO1', 'ALIADO1', 'ALIADO2', 'ALIADO2'],
        'codigo': ['CF001', 'CF002', 'CF003', 'CF001', 'CF002'],
        'nombre_cargo_fijo': ['Admin', 'Seguro', 'Mantenimiento', 'Admin', 'Seguro'],
        'valor': [50000, 100000, 200000, 60000, 120000],
        'periodicidad': ['MENSUAL', 'TRIMESTRAL', 'ANUAL', 'MENSUAL', 'TRIMESTRAL'],
        'placa': ['ABC123', 'ABC123', 'ABC123', 'XYZ789', 'XYZ789'],
        'cod_fasecolda': ['F001', 'F001', 'F001', 'F002', 'F002']
    }
    
    df = pd.DataFrame(data)
    
    # Crear cliente y procesar
    client = DataFrameAPIClient(desembolso_key='referencia', garantia_key='placa')
    
    # Validar
    validacion = client.validar_dataframe(df)
    print("Validación:", validacion)
    
    # Procesar
    resultado = client.procesar_dataframe(df)
    
    # Mostrar resumen
    resumen = client.obtener_resumen(resultado)
    print("\nResumen:", resumen)
    
    # Mostrar JSONs generados
    print("\n=== DESEMBOLSOS ===")
    for desembolso in resultado['desembolsos']:
        print(json.dumps(desembolso, indent=2, ensure_ascii=False))
    
    print("\n=== CARGOS FIJOS ===")
    for cargo in resultado['cargos_fijos']:
        print(json.dumps(cargo, indent=2, ensure_ascii=False))
    
    print("\n=== GARANTÍAS ===")
    for garantia in resultado['garantias']:
        print(json.dumps(garantia, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    ejemplo_uso()

