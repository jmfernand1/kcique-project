# 🚀 Inicio Rápido - API Dexter

## ✅ Verificación Completada

Todos los componentes de la API Dexter están correctamente instalados y configurados.

## 📋 Endpoints Disponibles

Una vez que inicies el servidor, tendrás acceso a:

### API REST Navegable
```
http://localhost:8000/dexter/api/
```

### Endpoints Principales

**Desembolsos:**
- `http://localhost:8000/dexter/api/desembolsos/` - CRUD completo
- `http://localhost:8000/dexter/api/desembolsos/{id}/cargos_fijos/` - Cargos fijos

**Cargos Fijos:**
- `http://localhost:8000/dexter/api/cargos-fijos/` - CRUD completo

**Garantías:**
- `http://localhost:8000/dexter/api/garantias/` - CRUD completo

## 🏃 Cómo Iniciar

### 1. Iniciar el Servidor Django

```bash
cd /Users/jmanuelf2/Documents/jobsProjects/kcique_project
python manage.py runserver
```

### 2. Probar en el Navegador

Abre tu navegador y ve a:
```
http://localhost:8000/dexter/api/
```

Verás la interfaz navegable de Django REST Framework donde puedes:
- Ver todos los endpoints disponibles
- Probar crear, leer, actualizar y eliminar registros
- Ver la documentación automática de cada endpoint

## 💻 Uso desde Python (ETL)

### Ejemplo Rápido

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# CREAR un desembolso
response = requests.post(
    f"{BASE_URL}/desembolsos/",
    json={
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
    }
)
desembolso = response.json()
print(f"✅ Desembolso creado con ID: {desembolso['id']}")

# LISTAR todos los desembolsos
response = requests.get(f"{BASE_URL}/desembolsos/")
data = response.json()
print(f"Total de desembolsos: {data['count']}")

# FILTRAR por aliado
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"aliado": "MI_ALIADO"}
)
filtrados = response.json()
print(f"Desembolsos filtrados: {filtrados['count']}")

# ACTUALIZAR un desembolso (parcialmente)
response = requests.patch(
    f"{BASE_URL}/desembolsos/{desembolso['id']}/",
    json={"valor_desembolso": 12000000.00}
)
actualizado = response.json()
print(f"✅ Valor actualizado: {actualizado['valor_desembolso']}")

# OBTENER un desembolso específico
response = requests.get(f"{BASE_URL}/desembolsos/{desembolso['id']}/")
detalle = response.json()
print(f"Desembolso: {detalle['referencia']}")

# ELIMINAR un desembolso
response = requests.delete(f"{BASE_URL}/desembolsos/{desembolso['id']}/")
if response.status_code == 204:
    print("✅ Desembolso eliminado")
```

### Cliente Completo

Para un cliente completo con todas las funcionalidades, usa:

```bash
python dexter/ejemplo_uso_api.py
```

Este archivo incluye:
- Clase `DexterAPIClient` con todos los métodos CRUD
- Ejemplos completos de uso
- Ejemplo de ETL básico
- Manejo de errores

## 📊 Ejemplos de Operaciones Comunes

### Crear Desembolso + Cargo Fijo

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# 1. Crear desembolso
desembolso_data = {
    "referencia": "DES-2025-100",
    "obligacion": 111111111,
    "id_cliente": 222222222,
    "nit_beneficiario": 900111111,
    "aliado": "PARTNER_A",
    "tipo_cta_destino": "Ahorros",
    "cod_tipo_cuenta_destino": 1,
    "num_cta_destino": 9876543210,
    "banco_destino": "Banco Nacional",
    "cod_banco_destino": 52,
    "valor_desembolso": 5000000.00,
    "numero_tramos": 1,
    "plazo_tramo_1": 24,
    "tipo_tasa_tramo_1": "EA",
    "tasa_tramo_1": 18.0,
    "amortizacion_tramo_1": "FRANCESA",
    "plazo_tramo_2": 0,
    "tipo_tasa_tramo_2": "EA",
    "tasa_tramo_2": 0.0,
    "amortizacion_tramo_2": "FRANCESA"
}

response = requests.post(f"{BASE_URL}/desembolsos/", json=desembolso_data)
desembolso = response.json()
desembolso_id = desembolso['id']

# 2. Agregar cargo fijo
cargo_data = {
    "desembolso": desembolso_id,
    "codigo": "CF001",
    "nombre_cargo_fijo": "Administración Mensual",
    "fecha_efectiva": "2025-01-01",
    "periodicidad": "MENSUAL",
    "valor": 50000.00
}

response = requests.post(f"{BASE_URL}/cargos-fijos/", json=cargo_data)
cargo = response.json()

print(f"✅ Desembolso {desembolso_id} con cargo fijo {cargo['id']}")

# 3. Consultar cargos del desembolso
response = requests.get(f"{BASE_URL}/desembolsos/{desembolso_id}/cargos_fijos/")
cargos = response.json()
print(f"Cargos fijos: {len(cargos)}")
```

### Crear Garantía

```python
import requests
from datetime import date

BASE_URL = "http://localhost:8000/dexter/api"

garantia_data = {
    "referencia": "DES-2025-100",
    "obligacion": 111111111,
    "id_cliente": 222222222,
    "id_garante": 222222222,
    "cod_fasecolda": "1234",
    "codigo_fasecolda": "5678",
    "color": "BLANCO",
    "placa": "XYZ789",
    "modelo": "2024",
    "valor_vehiculo": 45000000,
    "chasis": "CHASIS123456",
    "motor": "MOTOR123456",
    "fecha_desembolso": date.today().isoformat()
}

response = requests.post(f"{BASE_URL}/garantias/", json=garantia_data)
garantia = response.json()
print(f"✅ Garantía creada: {garantia['placa']}")
```

### Buscar y Filtrar

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Buscar por texto (búsqueda full-text)
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"search": "Banco Nacional"}
)

# Filtrar por múltiples campos
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={
        "aliado": "PARTNER_A",
        "referencia": "DES-2025-100"
    }
)

# Ordenar resultados
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"ordering": "-valor_desembolso"}  # Descendente
)

# Paginación
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"page": 2}
)

data = response.json()
print(f"Página actual: {data['count']} total")
print(f"Siguiente: {data['next']}")
print(f"Anterior: {data['previous']}")
```

## 🔧 Integración con Pandas (ETL)

```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/dexter/api"

# Leer CSV con datos de origen
df = pd.read_csv("desembolsos_origen.csv")

# Procesar cada fila
for index, row in df.iterrows():
    datos = {
        "referencia": row['referencia'],
        "obligacion": int(row['obligacion']),
        "id_cliente": int(row['id_cliente']),
        "nit_beneficiario": int(row['nit_beneficiario']),
        "aliado": row['aliado'],
        "tipo_cta_destino": row['tipo_cuenta'],
        "cod_tipo_cuenta_destino": int(row['cod_tipo_cuenta']),
        "num_cta_destino": int(row['num_cuenta']),
        "banco_destino": row['banco'],
        "cod_banco_destino": int(row['cod_banco']),
        "valor_desembolso": float(row['valor']),
        "numero_tramos": int(row['tramos']),
        "plazo_tramo_1": int(row['plazo_1']),
        "tipo_tasa_tramo_1": row['tipo_tasa_1'],
        "tasa_tramo_1": float(row['tasa_1']),
        "amortizacion_tramo_1": row['amortizacion_1'],
        "plazo_tramo_2": int(row.get('plazo_2', 0)),
        "tipo_tasa_tramo_2": row.get('tipo_tasa_2', 'EA'),
        "tasa_tramo_2": float(row.get('tasa_2', 0.0)),
        "amortizacion_tramo_2": row.get('amortizacion_2', 'FRANCESA')
    }
    
    try:
        response = requests.post(f"{BASE_URL}/desembolsos/", json=datos)
        response.raise_for_status()
        print(f"✅ Fila {index + 1}: {row['referencia']}")
    except Exception as e:
        print(f"❌ Fila {index + 1}: Error - {e}")
```

## 🎯 Consejos Importantes

### 1. Manejo de Errores

```python
import requests

try:
    response = requests.post(f"{BASE_URL}/desembolsos/", json=datos)
    response.raise_for_status()  # Lanza excepción si hay error HTTP
    resultado = response.json()
except requests.exceptions.HTTPError as e:
    print(f"Error HTTP: {e}")
    print(f"Detalles: {response.json()}")
except requests.exceptions.ConnectionError:
    print("Error de conexión. ¿El servidor está corriendo?")
except Exception as e:
    print(f"Error inesperado: {e}")
```

### 2. Validación de Datos

Antes de enviar datos, valida que:
- Los campos obligatorios estén presentes
- Los tipos de datos sean correctos
- Las referencias sean únicas

### 3. Rendimiento

Para cargas masivas:
- Usa paginación al consultar
- Procesa en lotes pequeños
- Implementa reintentos en caso de error
- Considera usar async/await para mayor velocidad

## 📚 Documentación Adicional

- **README completo**: `dexter/README.md`
- **Cliente Python**: `dexter/ejemplo_uso_api.py`
- **Resumen de implementación**: `DEXTER_API_RESUMEN.md`
- **Verificación**: `python verificar_dexter.py`

## 🆘 Solución de Problemas

### El servidor no inicia
```bash
python manage.py check  # Verificar problemas
python manage.py migrate  # Aplicar migraciones pendientes
```

### Error de conexión
- Asegúrate de que el servidor esté corriendo
- Verifica la URL base (http://localhost:8000)
- Revisa que no haya firewall bloqueando

### Error 400 (Bad Request)
- Revisa que los datos enviados sean correctos
- Verifica los tipos de datos (int, float, str)
- Asegúrate de enviar todos los campos obligatorios

### Error 404 (Not Found)
- Verifica la URL del endpoint
- Asegúrate de que el ID existe

### Error 500 (Internal Server Error)
- Revisa los logs del servidor Django
- Verifica la configuración de la base de datos

## ✅ Lista de Verificación

Antes de usar en producción:

- [ ] Migraciones aplicadas (`python manage.py migrate`)
- [ ] Servidor iniciado (`python manage.py runserver`)
- [ ] API accesible en el navegador
- [ ] Script de verificación ejecutado exitosamente
- [ ] Pruebas básicas realizadas
- [ ] Documentación revisada

## 🎉 ¡Listo para Usar!

Tu API REST de Dexter está completamente configurada y lista para recibir datos de tu ETL.

**¡Comienza ahora!**
```bash
python manage.py runserver
```

