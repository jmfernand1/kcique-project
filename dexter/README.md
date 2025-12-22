# Dexter - Sistema Completo de ETL y Tracking

## 📋 Descripción

**Dexter** es una aplicación Django completa que proporciona:
- 🎨 **Frontend Web**: Interfaz visual moderna para monitoreo y seguimiento de procesos ETL
- 🔌 **API REST**: API completa para la gestión programática de desembolsos, cargos fijos y garantías
- 📊 **Sistema de Tracking Avanzado**: Seguimiento detallado de cada ejecución ETL con plan de ejecución completo y retomado automático

Diseñada para integrarse perfectamente con procesos ETL (Extract, Transform, Load) en Python, permitiendo tanto la operación manual como automatizada.

---

## 🏗️ Arquitectura del Sistema

### Estructura de Capas

```
dexter/
├── models.py          # Estructura de datos (Django ORM)
├── services.py        # Lógica de negocio (crear plan, avanzar etapas, etc.)
├── viewsets.py        # Endpoints API (llama a services)
├── serializers.py     # Serialización de datos
├── admin.py           # Admin Django
└── views.py           # Vistas HTML para frontend
```

### Principios de Diseño

1. **Separación de responsabilidades**: ViewSets solo manejan HTTP, servicios manejan lógica
2. **Plan de ejecución completo**: Al iniciar una ejecución, se crean todas las etapas predefinidas
3. **Retomado automático**: Si la ETL falla, puede retomar desde la última etapa completada
4. **Tracking granular**: Cada etapa individual tiene su propio estado, intentos y errores

---

## 🗄️ Modelos de Datos

### Modelos de Tracking ETL

#### EjecucionETL
Registra cada ejecución completa del ETL con:
- Tipo de proceso (DESEMBOLSO o GARANTIA)
- Estado (INICIADO, EN_PROGRESO, COMPLETADO, FALLIDO, PAUSADO)
- Contadores de registros totales, procesados, exitosos y fallidos
- Fechas de inicio y fin
- Descripción y mensajes de error

#### ProcesoDesembolso / ProcesoGarantia
Contenedores principales que agrupan todas las etapas de un proceso:
- Estado general (PENDIENTE, EN_PROGRESO, COMPLETADO, ERROR, PAUSADO)
- Relación con ejecución y desembolso/garantía
- Métodos helper: `etapa_actual`, `siguiente_etapa`, `marcar_como_completado()`

#### EtapaProcesoDesembolso / EtapaProcesoGarantia
Representa cada etapa individual del proceso:
- Estado (PENDIENTE, EN_PROGRESO, COMPLETADO, ERROR, OMITIDA)
- Orden de ejecución
- Intentos y mensajes de error
- Datos específicos de la etapa (JSONField)
- Fechas de inicio y completado
- Métodos: `iniciar()`, `completar()`, `marcar_error()`

#### TipoDesembolso / TipoGarantia
Define los tipos de procesos y sus etapas:
- Nombre y descripción
- Relación con EtapaTipoDesembolso / EtapaTipoGarantia

#### EtapaTipoDesembolso / EtapaTipoGarantia
Define las etapas disponibles para cada tipo:
- Nombre y descripción
- Orden de ejecución
- Relación con TipoDesembolso / TipoGarantia

### Modelos de Datos Principales

#### Desembolso
Modelo principal que almacena información de desembolsos financieros.

**Campos principales:**
- `referencia` - Referencia única del desembolso
- `obligacion` - Número de obligación
- `id_cliente` - ID del cliente
- `nit_beneficiario` - NIT del beneficiario
- `aliado` - Nombre del aliado comercial
- `valor_desembolso` - Valor del desembolso
- `numero_tramos` - Número de tramos (1 o 2)
- `tipo_desembolso` - Relación con TipoDesembolso
- Información de cuenta destino
- Información de tramos (plazo, tasa, amortización)

#### CargoFijo
Cargos fijos asociados a un desembolso (relación ForeignKey).

**Campos principales:**
- `desembolso` - Relación con Desembolso
- `codigo` - Código del cargo
- `nombre_cargo_fijo` - Nombre descriptivo
- `fecha_efectiva` - Fecha de efectividad
- `periodicidad` - Frecuencia del cargo
- `valor` - Valor del cargo

#### Garantía
Información de garantías vehiculares asociadas a obligaciones.

**Campos principales:**
- `referencia` - Referencia del desembolso
- `obligacion` - Número de obligación
- `placa` - Placa del vehículo
- `modelo` - Año del modelo
- `valor_vehiculo` - Valor del vehículo
- Información FASECOLDA
- Información de seguro
- Datos técnicos del vehículo

---

## 🚀 Inicio Rápido

### 1. Migraciones

```bash
python manage.py makemigrations dexter
python manage.py migrate dexter
```

### 2. Iniciar el Servidor

```bash
python manage.py runserver
```

### 3. Acceder a la Aplicación

- **Dashboard Principal**: http://localhost:8000/dexter/
- **Lista de Ejecuciones**: http://localhost:8000/dexter/ejecuciones/
- **API Navegable**: http://localhost:8000/dexter/api/
- **Admin Django**: http://localhost:8000/admin/

### 4. Crear Datos de Prueba

```bash
python manage.py shell
```

```python
from dexter.crear_datos_prueba import crear_datos_prueba
crear_datos_prueba()
```

---

## 🔌 API REST - Documentación Completa

### URL Base
```
http://localhost:8000/dexter/api/
```

---

## 📊 Endpoints de Tracking ETL

### Ejecuciones ETL

#### 1. Crear Ejecución con Plan Completo

**Endpoint:** `POST /ejecuciones/crear_con_plan/`

**Cuerpo:**
```json
{
  "tipo_proceso": "DESEMBOLSO",
  "total_registros": 100,
  "descripcion": "ETL de desembolsos - Lote 001",
  "desembolso_ids": [1, 2, 3, 4, 5]
}
```

**Respuesta:**
```json
{
  "id": 1,
  "tipo_proceso": "DESEMBOLSO",
  "estado": "EN_PROGRESO",
  "total_registros": 100,
  "registros_procesados": 0,
  "registros_exitosos": 0,
  "registros_fallidos": 0,
  "progreso": 0.0,
  "fecha_inicio": "2025-01-15T10:00:00Z",
  "descripcion": "ETL de desembolsos - Lote 001"
}
```

**Nota:** Este endpoint crea automáticamente:
- La ejecución ETL
- Un ProcesoDesembolso/ProcesoGarantia para cada registro
- Todas las EtapaProcesoDesembolso/EtapaProcesoGarantia según el tipo configurado

#### 2. Obtener Ejecuciones Pendientes

**Endpoint:** `GET /ejecuciones/pendientes/`

**Parámetros opcionales:**
- `tipo_proceso`: DESEMBOLSO o GARANTIA

**Ejemplo:**
```
GET /ejecuciones/pendientes/?tipo_proceso=DESEMBOLSO
```

#### 3. Retomar Ejecución

**Endpoint:** `POST /ejecuciones/{id}/retomar/`

Marca una ejecución pausada o fallida como EN_PROGRESO.

#### 4. Obtener Progreso de Ejecución

**Endpoint:** `GET /ejecuciones/{id}/progreso/`

**Respuesta:**
```json
{
  "ejecucion_id": 1,
  "tipo_proceso": "DESEMBOLSO",
  "estado": "EN_PROGRESO",
  "total_registros": 100,
  "registros_procesados": 45,
  "registros_exitosos": 43,
  "registros_fallidos": 2,
  "progreso_porcentaje": 45.0,
  "distribucion_etapas": {
    "Grabar Cargos Fijos (PENDIENTE)": 55,
    "Desembolso (EN_PROGRESO)": 10,
    "Fraccionar (COMPLETADO)": 8,
    "Completado (COMPLETADO)": 43,
    "Error (ERROR)": 2
  }
}
```

#### 5. Completar Ejecución

**Endpoint:** `POST /ejecuciones/{id}/completar/`

#### 6. Marcar Ejecución como Fallida

**Endpoint:** `POST /ejecuciones/{id}/fallar/`

**Cuerpo:**
```json
{
  "mensaje_error": "Error en conexión a base de datos externa"
}
```

---

### Procesos de Desembolso

#### 1. Listar Procesos

**Endpoint:** `GET /procesos-desembolso/`

**Filtros disponibles:**
- `ejecucion` - ID de ejecución
- `estado_general` - Estado del proceso
- `desembolso` - ID de desembolso

**Respuesta incluye:**
- Información del proceso
- Lista completa de etapas con sus estados
- `etapa_actual_info` - Información de la etapa actual
- `siguiente_etapa_info` - Información de la siguiente etapa pendiente

#### 2. Obtener Siguiente Etapa

**Endpoint:** `GET /procesos-desembolso/{id}/siguiente_etapa/`

Retorna la siguiente etapa pendiente del proceso, o 204 si todas están completadas.

---

### Etapas de Proceso Desembolso

#### 1. Iniciar Etapa

**Endpoint:** `POST /etapas-proceso-desembolso/{id}/iniciar/`

Marca la etapa como EN_PROGRESO y actualiza el estado del proceso.

**Respuesta:**
```json
{
  "id": 123,
  "proceso": 1,
  "etapa": 5,
  "etapa_nombre": "Grabar Cargos Fijos",
  "orden": 1,
  "estado": "EN_PROGRESO",
  "fecha_inicio": "2025-01-15T10:05:00Z",
  "intentos": 1
}
```

#### 2. Completar Etapa

**Endpoint:** `POST /etapas-proceso-desembolso/{id}/completar/`

**Cuerpo:**
```json
{
  "datos_etapa": {
    "cargos_creados": 3,
    "tiempo_ejecucion": "2.5s"
  }
}
```

**Comportamiento:**
- Marca la etapa como COMPLETADO
- Avanza automáticamente a la siguiente etapa pendiente
- Si es la última etapa, marca el proceso como COMPLETADO
- Actualiza los contadores de la ejecución

#### 3. Marcar Error

**Endpoint:** `POST /etapas-proceso-desembolso/{id}/marcar_error/`

**Cuerpo:**
```json
{
  "mensaje_error": "Error al conectar con servicio externo",
  "datos_etapa": {
    "intento": 1,
    "error_code": "CONNECTION_TIMEOUT"
  }
}
```

**Comportamiento:**
- Marca la etapa como ERROR
- No avanza a la siguiente etapa
- Incrementa el contador de errores de la ejecución

#### 4. Reintentar Etapa

**Endpoint:** `POST /etapas-proceso-desembolso/{id}/reintentar/`

**Comportamiento:**
- Solo funciona para etapas con estado ERROR
- Limpia el mensaje de error
- Marca la etapa como EN_PROGRESO
- Incrementa el contador de intentos

---

### Procesos de Garantía

Los endpoints son similares a los de Desembolso:

- `GET /procesos-garantia/`
- `GET /procesos-garantia/{id}/siguiente_etapa/`

---

### Etapas de Proceso Garantía

Los endpoints son similares a los de Desembolso:

- `POST /etapas-proceso-garantia/{id}/iniciar/`
- `POST /etapas-proceso-garantia/{id}/completar/`
- `POST /etapas-proceso-garantia/{id}/marcar_error/`
- `POST /etapas-proceso-garantia/{id}/reintentar/`

---

## 💡 Flujo de Trabajo Completo

### Paso 1: Configurar Tipos y Etapas

Antes de usar el sistema, debes configurar los tipos de desembolso/garantía y sus etapas:

```python
# En Django Admin o vía API
# 1. Crear TipoDesembolso
tipo = TipoDesembolso.objects.create(
    nombre="Desembolso Estándar",
    descripcion="Proceso estándar de desembolso"
)

# 2. Crear Etapas en orden
EtapaTipoDesembolso.objects.create(
    nombre="Grabar Cargos Fijos",
    descripcion="Grabar los cargos fijos del desembolso",
    orden=1,
    tipo_desembolso=tipo
)

EtapaTipoDesembolso.objects.create(
    nombre="Desembolso",
    descripcion="Realizar el desembolso",
    orden=2,
    tipo_desembolso=tipo
)

# ... más etapas
```

### Paso 2: Crear Ejecución con Plan

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Obtener IDs de desembolsos a procesar
desembolso_ids = [1, 2, 3, 4, 5]

# Crear ejecución con plan completo
response = requests.post(f"{BASE_URL}/ejecuciones/crear_con_plan/", json={
    "tipo_proceso": "DESEMBOLSO",
    "total_registros": len(desembolso_ids),
    "descripcion": "ETL Desembolsos - Batch 001",
    "desembolso_ids": desembolso_ids
})

ejecucion = response.json()
ejecucion_id = ejecucion['id']
print(f"✅ Ejecución creada: {ejecucion_id}")
```

### Paso 3: Procesar Cada Registro

```python
# Obtener procesos pendientes
response = requests.get(
    f"{BASE_URL}/procesos-desembolso/",
    params={"ejecucion": ejecucion_id, "estado_general": "PENDIENTE"}
)

procesos = response.json()['results']

for proceso in procesos:
    proceso_id = proceso['id']
    desembolso_id = proceso['desembolso']
    
    # Obtener siguiente etapa
    response = requests.get(
        f"{BASE_URL}/procesos-desembolso/{proceso_id}/siguiente_etapa/"
    )
    
    if response.status_code == 200:
        etapa = response.json()
        etapa_id = etapa['id']
        etapa_nombre = etapa['etapa_nombre']
        
        # Iniciar etapa
        requests.post(f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/iniciar/")
        
        try:
            # Ejecutar lógica de la etapa
            if etapa_nombre == "Grabar Cargos Fijos":
                resultado = grabar_cargos_fijos(desembolso_id)
            elif etapa_nombre == "Desembolso":
                resultado = realizar_desembolso(desembolso_id)
            # ... más etapas
            
            # Completar etapa
            requests.post(
                f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/completar/",
                json={"datos_etapa": resultado}
            )
            
        except Exception as e:
            # Marcar error
            requests.post(
                f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/marcar_error/",
                json={"mensaje_error": str(e)}
            )
```

### Paso 4: Retomar Ejecución Fallida

```python
# Obtener ejecuciones pendientes
response = requests.get(
    f"{BASE_URL}/ejecuciones/pendientes/",
    params={"tipo_proceso": "DESEMBOLSO"}
)

pendientes = response.json()

if pendientes:
    ejecucion_id = pendientes[0]['id']
    
    # Retomar ejecución
    requests.post(f"{BASE_URL}/ejecuciones/{ejecucion_id}/retomar/")
    
    # Obtener procesos con errores
    response = requests.get(
        f"{BASE_URL}/procesos-desembolso/",
        params={"ejecucion": ejecucion_id, "estado_general": "ERROR"}
    )
    
    procesos_error = response.json()['results']
    
    for proceso in procesos_error:
        # Obtener etapa con error
        etapas = proceso['etapas']
        etapa_error = next((e for e in etapas if e['estado'] == 'ERROR'), None)
        
        if etapa_error:
            # Reintentar
            requests.post(
                f"{BASE_URL}/etapas-proceso-desembolso/{etapa_error['id']}/reintentar/"
            )
            
            # Continuar procesamiento...
```

---

## 🎨 Frontend Web

### Dashboard Principal (`/dexter/`)

Vista general con:
- **Estadísticas en tiempo real:**
  - Total de ejecuciones
  - Ejecuciones en progreso
  - Ejecuciones completadas
  - Ejecuciones fallidas
  - Ejecuciones iniciadas
  - Ejecuciones pausadas
  - Total de procesos de desembolso
  - Total de procesos de garantía

- **Métricas de rendimiento:**
  - Promedio de tiempo de ejecución para procesos completados

- **Ejecuciones recientes:**
  - Lista de las 10 ejecuciones más recientes
  - Barra de progreso visual para cada ejecución
  - Acceso rápido a los detalles

### Lista de Ejecuciones (`/dexter/ejecuciones/`)

Vista completa con:
- **Filtros avanzados:**
  - Búsqueda por texto (tipo, descripción, estado)
  - Filtro por tipo de proceso (Desembolso/Garantía)
  - Filtro por estado (Iniciado/En Progreso/Completado/Fallido/Pausado)

- **Información detallada:**
  - ID de ejecución
  - Tipo de proceso
  - Estado actual
  - Fechas de inicio y fin
  - Progreso visual (barra de progreso)
  - Registros totales, exitosos y fallidos

- **Paginación:**
  - 20 ejecuciones por página
  - Navegación fácil entre páginas

### Detalle de Ejecución (`/dexter/ejecuciones/<id>/`)

Vista detallada que muestra:

#### Información General
- ID y tipo de proceso
- Estado actual
- Fechas de inicio y fin
- Progreso total (% y números)
- Descripción y mensajes de error (si existen)

#### Distribución por Etapas
Tarjetas visuales mostrando cuántos procesos hay en cada etapa con su estado.

#### Listado de Procesos Individuales
Tabla detallada con cada caso individual:
- Referencia/Placa
- Obligación
- Etapa actual
- Fechas de inicio y última actualización
- Número de intentos
- Estado y errores (modal con detalles)

### Características de UX/UI

✅ **Diseño consistente** con la aplicación Adagio
✅ **Responsive** - funciona en desktop y móvil
✅ **Barras de progreso** animadas
✅ **Badges de color** para estados
✅ **Modales** para información detallada
✅ **Iconos Font Awesome** para mejor comprensión
✅ **Filtros en tiempo real** sin recargar página

---

## 🔌 Endpoints de Datos Principales

### Desembolsos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/desembolsos/` | Listar todos los desembolsos (paginado) |
| POST | `/desembolsos/` | Crear un nuevo desembolso |
| GET | `/desembolsos/{id}/` | Obtener un desembolso específico |
| PUT | `/desembolsos/{id}/` | Actualizar un desembolso completo |
| PATCH | `/desembolsos/{id}/` | Actualizar parcialmente un desembolso |
| DELETE | `/desembolsos/{id}/` | Eliminar un desembolso |
| GET | `/desembolsos/{id}/cargos_fijos/` | Obtener cargos fijos de un desembolso |

**Filtros disponibles:**
- `referencia` - Filtrar por referencia
- `obligacion` - Filtrar por obligación
- `id_cliente` - Filtrar por cliente
- `nit_beneficiario` - Filtrar por NIT
- `aliado` - Filtrar por aliado

**Búsqueda:**
- Buscar en: `referencia`, `aliado`, `banco_destino`

**Ordenamiento:**
- Campos: `id`, `referencia`, `valor_desembolso`

### Cargos Fijos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/cargos-fijos/` | Listar todos los cargos fijos |
| POST | `/cargos-fijos/` | Crear un nuevo cargo fijo |
| GET | `/cargos-fijos/{id}/` | Obtener un cargo fijo específico |
| PUT | `/cargos-fijos/{id}/` | Actualizar un cargo fijo completo |
| PATCH | `/cargos-fijos/{id}/` | Actualizar parcialmente un cargo fijo |
| DELETE | `/cargos-fijos/{id}/` | Eliminar un cargo fijo |

**Filtros disponibles:**
- `desembolso` - Filtrar por ID de desembolso
- `codigo` - Filtrar por código
- `periodicidad` - Filtrar por periodicidad

### Garantías

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/garantias/` | Listar todas las garantías |
| POST | `/garantias/` | Crear una nueva garantía |
| GET | `/garantias/{id}/` | Obtener una garantía específica |
| PUT | `/garantias/{id}/` | Actualizar una garantía completa |
| PATCH | `/garantias/{id}/` | Actualizar parcialmente una garantía |
| DELETE | `/garantias/{id}/` | Eliminar una garantía |

**Filtros disponibles:**
- `referencia` - Filtrar por referencia
- `obligacion` - Filtrar por obligación
- `id_cliente` - Filtrar por cliente
- `id_garante` - Filtrar por garante
- `placa` - Filtrar por placa
- `cod_fasecolda` - Filtrar por código FASECOLDA
- `cod_aseguradora` - Filtrar por código de aseguradora

**Búsqueda:**
- Buscar en: `referencia`, `placa`, `chasis`, `motor`, `nro_poliza`

---

## 💻 Ejemplos de Uso

### Ejemplo Básico - Crear Desembolso

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

datos = {
    "referencia": "DES-2025-001",
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
    "tipo_desembolso": 1  # ID del tipo de desembolso
}

response = requests.post(f"{BASE_URL}/desembolsos/", json=datos)
desembolso = response.json()
print(f"Desembolso creado con ID: {desembolso['id']}")
```

### Ejemplo Completo - ETL con Tracking

```python
import requests
from typing import List

BASE_URL = "http://localhost:8000/dexter/api"

def ejecutar_etl_desembolso(desembolso_ids: List[int]):
    """Ejecuta un ETL completo con tracking"""
    
    # 1. Crear ejecución con plan
    response = requests.post(f"{BASE_URL}/ejecuciones/crear_con_plan/", json={
        "tipo_proceso": "DESEMBOLSO",
        "total_registros": len(desembolso_ids),
        "descripcion": "ETL Desembolsos - Batch 001",
        "desembolso_ids": desembolso_ids
    })
    ejecucion = response.json()
    ejecucion_id = ejecucion['id']
    
    # 2. Obtener procesos pendientes
    response = requests.get(
        f"{BASE_URL}/procesos-desembolso/",
        params={"ejecucion": ejecucion_id, "estado_general": "PENDIENTE"}
    )
    procesos = response.json()['results']
    
    # 3. Procesar cada desembolso
    for proceso in procesos:
        proceso_id = proceso['id']
        desembolso_id = proceso['desembolso']
        
        # Obtener siguiente etapa
        response = requests.get(
            f"{BASE_URL}/procesos-desembolso/{proceso_id}/siguiente_etapa/"
        )
        
        while response.status_code == 200:
            etapa = response.json()
            etapa_id = etapa['id']
            etapa_nombre = etapa['etapa_nombre']
            
            # Iniciar etapa
            requests.post(
                f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/iniciar/"
            )
            
            try:
                # Ejecutar lógica según la etapa
                resultado = ejecutar_etapa(desembolso_id, etapa_nombre)
                
                # Completar etapa
                requests.post(
                    f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/completar/",
                    json={"datos_etapa": resultado}
                )
                
            except Exception as e:
                # Marcar error
                requests.post(
                    f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/marcar_error/",
                    json={"mensaje_error": str(e)}
                )
                break  # Salir del loop de etapas para este proceso
            
            # Obtener siguiente etapa
            response = requests.get(
                f"{BASE_URL}/procesos-desembolso/{proceso_id}/siguiente_etapa/"
            )
    
    # 4. Verificar progreso
    response = requests.get(f"{BASE_URL}/ejecuciones/{ejecucion_id}/progreso/")
    progreso = response.json()
    print(f"Progreso: {progreso['progreso_porcentaje']}%")
    
    # 5. Completar ejecución
    if progreso['registros_procesados'] == progreso['total_registros']:
        requests.post(f"{BASE_URL}/ejecuciones/{ejecucion_id}/completar/")

def ejecutar_etapa(desembolso_id: int, etapa_nombre: str) -> dict:
    """Ejecuta la lógica de una etapa específica"""
    if etapa_nombre == "Grabar Cargos Fijos":
        return {"cargos_creados": 3}
    elif etapa_nombre == "Desembolso":
        return {"desembolso_realizado": True}
    # ... más etapas
    return {}
```

---

## 🛠️ Configuración

### Características de la API

#### Paginación
La API está paginada por defecto (10 elementos por página). Puedes navegar usando:
```
GET /desembolsos/?page=2
```

#### Filtros
Usa parámetros de query para filtrar:
```
GET /desembolsos/?aliado=ALIADO_PRUEBA&estado=ACTIVO
```

#### Búsqueda
Usa el parámetro `search` para buscar:
```
GET /desembolsos/?search=ABC123
```

#### Ordenamiento
Usa el parámetro `ordering` para ordenar:
```
GET /desembolsos/?ordering=-valor_desembolso  # Descendente
GET /desembolsos/?ordering=referencia          # Ascendente
```

### Autenticación (Opcional)

Si necesitas agregar autenticación a la API:

```python
# En settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

---

## 📝 Notas Importantes

1. **Referencia única**: El campo `referencia` en Desembolso debe ser único
2. **Relaciones**: Al eliminar un Desembolso, se eliminan automáticamente sus CargosFijos (CASCADE)
3. **Campos opcionales**: Muchos campos son opcionales (`null=True, blank=True`) para flexibilidad
4. **Validación**: La API valida automáticamente los datos según los modelos
5. **Plan de ejecución**: Las etapas se crean automáticamente al crear una ejecución con plan
6. **Retomado automático**: El sistema permite retomar desde la última etapa completada

---

## 🧪 Pruebas

Para probar la API, puedes usar:

1. **Navegador**: Accede a http://localhost:8000/dexter/api/
2. **Postman**: Importa la colección de endpoints
3. **cURL**: Ejemplos en línea de comandos
4. **Script Python**: Ejecuta `python ejemplo_uso_api.py`

### Ejemplo con cURL

```bash
# Crear desembolso
curl -X POST http://localhost:8000/dexter/api/desembolsos/ \
  -H "Content-Type: application/json" \
  -d '{"referencia":"DES-001","obligacion":123,"id_cliente":456,...}'

# Listar desembolsos
curl http://localhost:8000/dexter/api/desembolsos/

# Obtener un desembolso
curl http://localhost:8000/dexter/api/desembolsos/1/
```

---

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
- Verifica que el tipo_desembolso tenga etapas configuradas

### Error 404 (Not Found)
- Verifica la URL del endpoint
- Asegúrate de que el ID existe

### Error 500 (Internal Server Error)
- Revisa los logs del servidor Django
- Verifica la configuración de la base de datos

---

## 📚 Archivos de Referencia

- **Cliente Python completo**: `ejemplo_uso_api.py`
- **Script de datos de prueba**: `crear_datos_prueba.py`
- **Servicios de negocio**: `services.py`
- **Modelos**: `models.py`

---

## 📞 Soporte

Para más información sobre Django Rest Framework:
- [Documentación oficial](https://www.django-rest-framework.org/)
- [Tutorial de DRF](https://www.django-rest-framework.org/tutorial/quickstart/)

---

## 📄 Licencia

Este proyecto es parte del sistema Kcique.
