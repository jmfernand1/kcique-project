"""
Ejemplo de uso del DataFrameAPIClient para procesar DataFrames y enviar datos a la API.

Este ejemplo muestra cómo usar el cliente para procesar un DataFrame donde
la información de desembolso y garantía se repite según los cargos fijos.
"""

import pandas as pd
from dexter.dataframe_api_client import DataFrameAPIClientCompleto
import json


def ejemplo_basico():
    """Ejemplo básico: procesar DataFrame y generar JSONs."""
    print("=" * 60)
    print("EJEMPLO BÁSICO: Procesar DataFrame y generar JSONs")
    print("=" * 60)
    
    # Crear DataFrame de ejemplo
    # Nota: Cada fila representa un cargo fijo, pero repite info de desembolso/garantía
    data = {
        'referencia': ['DES-2025-001', 'DES-2025-001', 'DES-2025-001', 'DES-2025-002', 'DES-2025-002'],
        'obligacion': [123456789, 123456789, 123456789, 987654321, 987654321],
        'id_cliente': [1001, 1001, 1001, 1002, 1002],
        'nit_beneficiario': [900123456, 900123456, 900123456, 900789012, 900789012],
        'aliado': ['ALIADO_A', 'ALIADO_A', 'ALIADO_A', 'ALIADO_B', 'ALIADO_B'],
        'tipo_cta_destino': ['Ahorros', 'Ahorros', 'Ahorros', 'Corriente', 'Corriente'],
        'cod_tipo_cuenta_destino': [1, 1, 1, 2, 2],
        'num_cta_destino': [1234567890, 1234567890, 1234567890, 9876543210, 9876543210],
        'banco_destino': ['Banco Popular', 'Banco Popular', 'Banco Popular', 'Bancolombia', 'Bancolombia'],
        'cod_banco_destino': [51, 51, 51, 52, 52],
        'valor_desembolso': [50000000.0, 50000000.0, 50000000.0, 75000000.0, 75000000.0],
        'numero_tramos': [1, 1, 1, 2, 2],
        'plazo_tramo_1': [36, 36, 36, 48, 48],
        'tipo_tasa_tramo_1': ['EA', 'EA', 'EA', 'EA', 'EA'],
        'tasa_tramo_1': [18.5, 18.5, 18.5, 19.0, 19.0],
        'amortizacion_tramo_1': ['FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA'],
        'plazo_tramo_2': [0, 0, 0, 12, 12],
        'tipo_tasa_tramo_2': ['EA', 'EA', 'EA', 'EA', 'EA'],
        'tasa_tramo_2': [0.0, 0.0, 0.0, 16.5, 16.5],
        'amortizacion_tramo_2': ['FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA', 'FRANCESA'],
        'dia_pago_cuota': [15, 15, 15, 20, 20],
        'estado': ['PENDIENTE', 'PENDIENTE', 'PENDIENTE', 'PENDIENTE', 'PENDIENTE'],
        'observaciones': [
            '{"nota": "Cliente preferencial", "prioridad": "alta"}',
            '{"nota": "Cliente preferencial", "prioridad": "alta"}',
            '{"nota": "Cliente preferencial", "prioridad": "alta"}',
            '{"nota": "Requiere seguimiento especial", "contacto": "juan@example.com"}',
            '{"nota": "Requiere seguimiento especial", "contacto": "juan@example.com"}'
        ],
        # Columnas de SharePoint (se agrupan automáticamente en ids_sharepoint)
        # El cliente detecta columnas que empiecen con: id_sharepoint_, sharepoint_, sp_
        # y las agrupa en un diccionario. Ejemplo:
        # - id_sharepoint_documento_1 -> ids_sharepoint['documento_1']
        # - sharepoint_contrato -> ids_sharepoint['contrato']
        'id_sharepoint_documento_1': ['abc123', 'abc123', 'abc123', 'xyz789', 'xyz789'],
        'id_sharepoint_documento_2': ['def456', 'def456', 'def456', 'uvw012', 'uvw012'],
        'id_sharepoint_cedula': ['ced123', 'ced123', 'ced123', 'ced456', 'ced456'],
        'sharepoint_contrato': ['cont001', 'cont001', 'cont001', 'cont002', 'cont002'],
        
        # Campos de cargos fijos (varían por fila)
        'codigo': ['CF001', 'CF002', 'CF003', 'CF001', 'CF002'],
        'nombre_cargo_fijo': [
            'Administración Mensual',
            'Seguro Vehicular Trimestral',
            'Mantenimiento Anual',
            'Administración Mensual',
            'Seguro Vehicular Trimestral'
        ],
        'valor': [50000.0, 150000.0, 300000.0, 60000.0, 180000.0],
        'periodicidad': ['MENSUAL', 'TRIMESTRAL', 'ANUAL', 'MENSUAL', 'TRIMESTRAL'],
        'fecha_efectiva': ['2025-01-01', '2025-01-01', '2025-01-01', '2025-02-01', '2025-02-01'],
        
        # Campos de garantía (se repiten por desembolso)
        'placa': ['ABC123', 'ABC123', 'ABC123', 'XYZ789', 'XYZ789'],
        'cod_fasecolda': ['F001', 'F001', 'F001', 'F002', 'F002'],
        'codigo_fasecolda': ['F001', 'F001', 'F001', 'F002', 'F002'],
        'id_garante': [5001, 5001, 5001, 5002, 5002],
        'color': ['Rojo', 'Rojo', 'Rojo', 'Azul', 'Azul'],
        'valor_vehiculo': [60000000, 60000000, 60000000, 80000000, 80000000],
        'modelo': ['2023', '2023', '2023', '2024', '2024']
    }
    
    df = pd.DataFrame(data)
    
    # Crear cliente
    client = DataFrameAPIClientCompleto(
        base_url="http://localhost:8000/dexter/api",
        desembolso_key='referencia',
        garantia_key='placa'
    )
    
    # Validar DataFrame
    print("\n1. Validando DataFrame...")
    validacion = client.validar_dataframe(df)
    if validacion['valido']:
        print("✅ DataFrame válido")
        print(f"   - Campos de desembolso encontrados: {len(validacion['campos_desembolso_encontrados'])}")
        print(f"   - Campos de cargo fijo encontrados: {len(validacion['campos_cargo_encontrados'])}")
    else:
        print("❌ Errores en el DataFrame:")
        for error in validacion['errores']:
            print(f"   - {error}")
        return
    
    # Procesar DataFrame
    print("\n2. Procesando DataFrame...")
    datos = client.procesar_solo_json(df)
    
    # Mostrar resumen
    resumen = client.obtener_resumen(datos)
    print("\n3. Resumen del procesamiento:")
    print(f"   - Desembolsos: {resumen['total_desembolsos']}")
    print(f"   - Cargos fijos: {resumen['total_cargos_fijos']}")
    print(f"   - Garantías: {resumen['total_garantias']}")
    print(f"   - Promedio cargos por desembolso: {resumen['cargos_fijos_por_desembolso']:.2f}")
    
    # Mostrar JSONs generados
    print("\n4. JSONs generados:")
    print("\n--- DESEMBOLSO 1 ---")
    print(json.dumps(datos['desembolsos'][0], indent=2, ensure_ascii=False))
    
    print("\n--- CARGOS FIJOS ---")
    for i, cargo in enumerate(datos['cargos_fijos'][:3], 1):
        print(f"\nCargo {i}:")
        print(json.dumps(cargo, indent=2, ensure_ascii=False))
    
    if datos['garantias']:
        print("\n--- GARANTÍA 1 ---")
        print(json.dumps(datos['garantias'][0], indent=2, ensure_ascii=False))


def ejemplo_enviar_a_api():
    """Ejemplo avanzado: procesar y enviar directamente a la API."""
    print("\n" + "=" * 60)
    print("EJEMPLO AVANZADO: Procesar y enviar a la API")
    print("=" * 60)
    
    # Crear DataFrame (similar al ejemplo anterior)
    data = {
        'referencia': ['DES-2025-TEST-001', 'DES-2025-TEST-001'],
        'obligacion': [999888777, 999888777],
        'id_cliente': [9999, 9999],
        'nit_beneficiario': [999999999, 999999999],
        'aliado': ['TEST_ALIADO', 'TEST_ALIADO'],
        'tipo_cta_destino': ['Ahorros', 'Ahorros'],
        'cod_tipo_cuenta_destino': [1, 1],
        'num_cta_destino': [9999999999, 9999999999],
        'banco_destino': ['Banco Test', 'Banco Test'],
        'cod_banco_destino': [99, 99],
        'valor_desembolso': [10000000.0, 10000000.0],
        'numero_tramos': [1, 1],
        'plazo_tramo_1': [12, 12],
        'tipo_tasa_tramo_1': ['EA', 'EA'],
        'tasa_tramo_1': [15.5, 15.5],
        'amortizacion_tramo_1': ['FRANCESA', 'FRANCESA'],
        'plazo_tramo_2': [0, 0],
        'tipo_tasa_tramo_2': ['EA', 'EA'],
        'tasa_tramo_2': [0.0, 0.0],
        'amortizacion_tramo_2': ['FRANCESA', 'FRANCESA'],
        'observaciones': [
            '{"tipo": "test", "ambiente": "desarrollo"}',
            '{"tipo": "test", "ambiente": "desarrollo"}'
        ],
        # Columnas de SharePoint (se agrupan automáticamente en ids_sharepoint)
        # El cliente detecta columnas que empiecen con: id_sharepoint_, sharepoint_, sp_
        'id_sharepoint_test_doc': ['test123', 'test123'],
        'sharepoint_archivo': ['archivo_test', 'archivo_test'],
        'codigo': ['CF-TEST-001', 'CF-TEST-002'],
        'nombre_cargo_fijo': ['Cargo Test 1', 'Cargo Test 2'],
        'valor': [10000.0, 20000.0],
        'periodicidad': ['MENSUAL', 'TRIMESTRAL'],
        'fecha_efectiva': ['2025-01-01', '2025-01-01']
    }
    
    df = pd.DataFrame(data)
    
    # Crear cliente
    client = DataFrameAPIClientCompleto(
        base_url="http://localhost:8000/dexter/api",
        desembolso_key='referencia'
    )
    
    print("\n⚠️  NOTA: Este ejemplo intentará enviar datos a la API.")
    print("   Asegúrate de que el servidor esté corriendo en http://localhost:8000")
    print("   Descomenta las líneas siguientes para ejecutar:\n")
    
    # Descomentar para ejecutar:
    print("\n1. Procesando y enviando a la API...")
    resultado = client.procesar_y_enviar(
        df,
        crear_garantias=False,  # No hay garantías en este ejemplo
        actualizar_existentes=False  # Solo crear nuevos
    )
    
    print("\n2. Resultado:")
    print(f"   ✅ Desembolsos creados: {len(resultado['desembolsos_creados'])}")
    print(f"   ✅ Cargos fijos creados: {len(resultado['cargos_fijos_creados'])}")
    if resultado['desembolsos_creados']:
        print(f"   IDs: {resultado['desembolsos_creados']}")
    if resultado['cargos_fijos_creados']:
        print(f"   IDs: {resultado['cargos_fijos_creados']}")
    
    if resultado['errores']:
        print(f"\n   ❌ Errores: {len(resultado['errores'])}")
        for error in resultado['errores']:
            print(f"      - {error}")


def ejemplo_desde_csv():
    """Ejemplo: cargar desde CSV y procesar."""
    print("\n" + "=" * 60)
    print("EJEMPLO: Cargar desde CSV")
    print("=" * 60)
    
    print("\nPara usar este ejemplo:")
    print("1. Crea un archivo CSV con las columnas necesarias")
    print("2. Asegúrate de que tenga al menos:")
    print("   - Una columna 'referencia' (o la que uses como clave)")
    print("   - Columnas de desembolso (obligacion, id_cliente, etc.)")
    print("   - Columnas de cargos fijos (codigo, nombre_cargo_fijo, valor, etc.)")
    print("   - Opcionalmente, columnas de garantía")
    print("\n3. Carga y procesa:")
    print("""
    import pandas as pd
    from dexter.dataframe_api_client import DataFrameAPIClientCompleto
    
    # Cargar CSV
    df = pd.read_csv('mi_archivo.csv')
    
    # Crear cliente
    client = DataFrameAPIClientCompleto(
        base_url="http://localhost:8000/dexter/api",
        desembolso_key='referencia'
    )
    
    # Validar
    validacion = client.validar_dataframe(df)
    if not validacion['valido']:
        print("Errores:", validacion['errores'])
    else:
        # Procesar y enviar
        resultado = client.procesar_y_enviar(df)
        print("Resultado:", resultado)
    """)


if __name__ == '__main__':
    # ejemplo_basico()
    ejemplo_enviar_a_api()
    # ejemplo_desde_csv()
    
    print("\n" + "=" * 60)
    print("✅ EJEMPLOS COMPLETADOS")
    print("=" * 60)

