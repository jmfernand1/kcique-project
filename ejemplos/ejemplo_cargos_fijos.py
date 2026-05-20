"""
Ejemplo corto: Crear cargos fijos usando la API de Dexter

Requisitos: pip install requests
Servidor: python manage.py runserver
"""

import requests
from datetime import date

BASE_URL = "http://localhost:8000/dexter/api"

print("=" * 60)
print("EJEMPLO: CREAR CARGOS FIJOS")
print("=" * 60)

# Paso 1: Crear un desembolso primero
for i in range(10):
    print(f"\n1️⃣ Creando desembolso {i+1}...")
    desembolso_data = {
        "referencia": f"DES-2025-TEST-00{i+1}",
        "obligacion": 123456789,
        "id_cliente": 987654321,
        "nit_beneficiario": 900123456,
        "aliado": "ALIADO_EJEMPLO",
        "tipo_cta_destino": "Ahorros",
        "cod_tipo_cuenta_destino": 1,
        "num_cta_destino": 1234567890,
        "banco_destino": "Banco Ejemplo",
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
        "estado": "PENDIENTE",
        "tipo_desembolso": 1
    }
    try:
        response = requests.post(f"{BASE_URL}/desembolsos/", json=desembolso_data)
        response.raise_for_status()
        desembolso = response.json()
        desembolso_id = desembolso['id']
        print(f"✅ Desembolso creado con ID: {desembolso_id}")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error al crear desembolso: {e}")
        print(response.json())
        exit()

    # Paso 2: Crear cargos fijos para ese desembolso
    print("\n2️⃣ Creando cargos fijos...")

    cargos = [
        {
            "desembolso": desembolso_id,
            "codigo": "CF001",
            "nombre_cargo_fijo": "Administración Mensual",
            "fecha_efectiva": date.today().isoformat(),
            "periodicidad": "MENSUAL",
            "valor": 50000.00
        },
        {
            "desembolso": desembolso_id,
            "codigo": "CF002",
            "nombre_cargo_fijo": "Seguro Trimestral",
            "fecha_efectiva": date.today().isoformat(),
            "periodicidad": "TRIMESTRAL",
            "valor": 150000.00
        },
        {
            "desembolso": desembolso_id,
            "codigo": "CF003",
            "nombre_cargo_fijo": "Mantenimiento Anual",
            "fecha_efectiva": date.today().isoformat(),
            "periodicidad": "ANUAL",
            "valor": 200000.00
        }
    ]

    for cargo_data in cargos:
        try:
            response = requests.post(f"{BASE_URL}/cargos-fijos/", json=cargo_data)
            response.raise_for_status()
            cargo = response.json()
            print(f"✅ {cargo['nombre_cargo_fijo']} - ID: {cargo['id']}")
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error al crear cargo fijo: {e}")
            print(response.json())
            exit()

    # Paso 3: Consultar los cargos del desembolso
    print("\n3️⃣ Consultando cargos fijos del desembolso...")
    response = requests.get(f"{BASE_URL}/desembolsos/{desembolso_id}/cargos_fijos/")
    cargos_resultado = response.json()

    print(f"\nTotal de cargos fijos: {len(cargos_resultado)}")
    for cargo in cargos_resultado:
        print(f"  - {cargo['nombre_cargo_fijo']}: ${cargo['valor']:,.2f} ({cargo['periodicidad']})")

    print("\n" + "=" * 60)
    print("✅ EJEMPLO COMPLETADO")
    print("=" * 60)
    print(f"\n💡 Tip: Puedes ver el desembolso con sus cargos en:")
    print(f"   http://localhost:8000/dexter/api/desembolsos/{desembolso_id}/")

