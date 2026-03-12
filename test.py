import requests

# hasta aca ya se tiene la extraccion de datos del sharepoint

desembolso_dic = [
    {
        "referencia": "DES-2025-TEST-001",
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
        "numero_tramos": 1,
        "plazo_tramo_1": 12,
        "tipo_tasa_tramo_1": "EA",
        "tasa_tramo_1": 15.5,
        "amortizacion_tramo_1": "FRANCESA",
        "plazo_tramo_2": 0,
        "tipo_tasa_tramo_2": "EA",
        "tasa_tramo_2": 0.0,
        "amortizacion_tramo_2": "FRANCESA",
        "dia_pago_cuota": 15,
        "estado": "PENDIENTE",
        "observaciones": {"nota": "Desembolso de prueba"},
        "ids_sharepoint": {
            "id_seguros": 1234567890,
            "id_desembolso": 1234567890,
            "id_garantia": 1234567890
        },
        "cargos_fijos": [
            {
                "codigo": "CF001",
                "nombre_cargo_fijo": "Administración Mensual",
                "fecha_efectiva": "2025-01-01",
                "fecha_revision": "2025-01-01",
                "periodicidad": "MENSUAL",
                "valor": 10000000.00
            },
            {
                "codigo": "CF002",
                "nombre_cargo_fijo": "Seguro Vehicular Trimestral",
                "fecha_efectiva": "2025-01-01",
                "fecha_revision": "2025-01-01",
                "periodicidad": "TRIMESTRAL",
                "valor": 150000.00
            }
        ]
    }
]

BASE_URL = "http://localhost:8000/dexter/api"

for desem in desembolso_dic:

    # Datos del desembolso
    datos_desembolso = {
        "referencia": desem['referencia'],
        "obligacion": desem['obligacion'],
        "id_cliente": desem['id_cliente'],
        "nit_beneficiario": desem['nit_beneficiario'],
        "aliado": desem['aliado'],
        "tipo_cta_destino": desem['tipo_cta_destino'],
        "cod_tipo_cuenta_destino": 1,
        "num_cta_destino": desem['num_cta_destino'],
        "banco_destino": "Banco de Prueba",
        "cod_banco_destino": desem['cod_banco_destino'],
        "valor_desembolso": desem['valor_desembolso'],
        "numero_tramos": desem['numero_tramos'],
        "plazo_tramo_1": desem['plazo_tramo_1'],
        "tipo_tasa_tramo_1": desem['tipo_tasa_tramo_1'],
        "tasa_tramo_1": desem['tasa_tramo_1'],
        "amortizacion_tramo_1": desem['amortizacion_tramo_1'],
        "plazo_tramo_2": desem['plazo_tramo_2'],
        "tipo_tasa_tramo_2": desem['tipo_tasa_tramo_2'],
        "tasa_tramo_2": desem['tasa_tramo_2'],
        "amortizacion_tramo_2": desem['amortizacion_tramo_2'],
        "dia_pago_cuota": desem['dia_pago_cuota'],
        "estado": "PENDIENTE",
        "observaciones": {"nota": "Desembolso de prueba"},
        "ids_sharepoint": desem['ids_sharepoint']
    }

    # Crear desembolso
    response = requests.post(
        f"{BASE_URL}/desembolsos/",
        json=datos_desembolso
    )

    print(response.json())

    if response.status_code == 201:
        desembolso = response.json()
        print(f"✅ Desembolso creado con ID: {desembolso['id']}")
        print(f"   Referencia: {desembolso['referencia']}")

        for cargo in desem['cargos_fijos']:
            cargo_data = {
                "desembolso": desembolso['id'],
                "codigo": cargo['codigo'],
                "nombre_cargo_fijo": cargo['nombre_cargo_fijo'],
                "fecha_efectiva": cargo['fecha_efectiva'],
                "fecha_revision": cargo['fecha_revision'],
                "periodicidad": cargo['periodicidad'],
                "valor": cargo['valor']
            }
            response = requests.post(
                f"{BASE_URL}/cargos-fijos/",
                json=cargo_data
            )
            if response.status_code == 201:
                cargo = response.json()
                print(f"✅ Cargo fijo creado con ID: {cargo['id']}")
                print(f"   Nombre: {cargo['nombre_cargo_fijo']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(response.json())
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.json())