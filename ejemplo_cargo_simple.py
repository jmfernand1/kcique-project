"""
Ejemplo SIMPLE: Crear un cargo fijo
(Asume que ya existe un desembolso con ID = 1)
"""

import requests
from datetime import date

BASE_URL = "http://localhost:8000/dexter/api"

# ID del desembolso al que quieres agregar el cargo
DESEMBOLSO_ID = 1  # 👈 Cambia este ID según tu desembolso

# Datos del cargo fijo
cargo_data = {
    "desembolso": DESEMBOLSO_ID,
    "codigo": "CF001",
    "nombre_cargo_fijo": "Administración Mensual",
    "fecha_efectiva": date.today().isoformat(),
    "periodicidad": "MENSUAL",
    "valor": 50000.00
}

# Crear el cargo fijo
response = requests.post(f"{BASE_URL}/cargos-fijos/", json=cargo_data)

if response.status_code == 201:
    cargo = response.json()
    print(f"✅ Cargo fijo creado exitosamente!")
    print(f"   ID: {cargo['id']}")
    print(f"   Nombre: {cargo['nombre_cargo_fijo']}")
    print(f"   Valor: ${cargo['valor']:,.2f}")
    print(f"   Periodicidad: {cargo['periodicidad']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())

