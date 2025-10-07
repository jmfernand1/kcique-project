import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Crear desembolso
response = requests.post(f"{BASE_URL}/desembolsos/", json={
    "referencia": "DES-2025-001",
    "obligacion": 123456789,
    "id_cliente": 987654321,
    "nit_beneficiario": 900123456,
    "aliado": "MI_ALIADO",
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
    "amortizacion_tramo_2": "FRANCESA"
})
desembolso = response.json()
print(f"Desembolso creado: ID {desembolso['id']}")

# Listar todos
response = requests.get(f"{BASE_URL}/desembolsos/")
print(f"Total: {response.json()['count']}")

# Filtrar
response = requests.get(f"{BASE_URL}/desembolsos/", 
                       params={"aliado": "MI_ALIADO"})

# Actualizar
requests.patch(f"{BASE_URL}/desembolsos/{desembolso['id']}/",
              json={"valor_desembolso": 12000000.00})