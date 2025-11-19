# 🎯 Guía de API de Tracking para ETL Externo

## 📋 Descripción

Sistema de tracking con checkpoints para procesos ETL que permite retomar ejecuciones desde donde quedaron en caso de fallo.

## 🚀 Endpoints Disponibles

### URL Base
```
http://localhost:8000/dexter/api/
```

---

## 📊 Ejecuciones ETL

### 1. Crear Nueva Ejecución

**Endpoint:** `POST /ejecuciones/`

**Cuerpo:**
```json
{
  "tipo_proceso": "DESEMBOLSO",  // o "GARANTIA"
  "estado": "EN_PROGRESO",
  "total_registros": 100,
  "descripcion": "ETL de desembolsos - Lote 001"
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
  "fecha_inicio": "2025-10-07T11:00:00Z",
  "descripcion": "ETL de desembolsos - Lote 001"
}
```

### 2. Obtener Ejecuciones Pendientes

**Endpoint:** `GET /ejecuciones/pendientes/`

**Parámetros opcionales:**
- `tipo_proceso`: DESEMBOLSO o GARANTIA

**Ejemplo:**
```
GET /ejecuciones/pendientes/?tipo_proceso=DESEMBOLSO
```

### 3. Obtener Progreso de Ejecución

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
    "Pendiente": 55,
    "Grabar Cargos Fijos": 10,
    "Desembolso": 8,
    "Completado": 43,
    "Error": 2
  }
}
```

### 4. Completar Ejecución

**Endpoint:** `POST /ejecuciones/{id}/completar/`

### 5. Marcar Ejecución como Fallida

**Endpoint:** `POST /ejecuciones/{id}/fallar/`

**Cuerpo:**
```json
{
  "mensaje_error": "Error en conexión a base de datos externa"
}
```

---

## 🔄 Procesos de Desembolso

### 1. Crear Proceso de Tracking

**Endpoint:** `POST /procesos-desembolso/`

**Cuerpo:**
```json
{
  "ejecucion": 1,
  "desembolso": 123,
  "etapa_actual": "PENDIENTE"
}
```

**Respuesta:**
```json
{
  "id": 1,
  "ejecucion": 1,
  "desembolso": 123,
  "desembolso_referencia": "DES-2025-001",
  "etapa_actual": "PENDIENTE",
  "intentos": 0,
  "mensaje_error": null,
  "datos_etapa": null
}
```

### 2. Avanzar a Siguiente Etapa

**Endpoint:** `POST /procesos-desembolso/{id}/avanzar_etapa/`

**Cuerpo:**
```json
{
  "etapa": "GRABAR_CARGOS_FIJOS",
  "datos_etapa": {
    "cargos_creados": 3,
    "tiempo_ejecucion": "2.5s"
  }
}
```

**Etapas válidas para desembolso:**
- `GRABAR_CARGOS_FIJOS`
- `DESEMBOLSO`
- `FRACCIONAR`
- `SELECCIONAR_PAGO`
- `AUTORIZAR`

### 3. Marcar Error

**Endpoint:** `POST /procesos-desembolso/{id}/marcar_error/`

**Cuerpo:**
```json
{
  "mensaje_error": "Error al conectar con servicio externo"
}
```

### 4. Completar Proceso

**Endpoint:** `POST /procesos-desembolso/{id}/completar/`

### 5. Listar Procesos Pendientes

**Endpoint:** `GET /procesos-desembolso/?ejecucion={id}&etapa_actual=PENDIENTE`

---

## 🚗 Procesos de Garantía

### 1. Crear Proceso de Tracking

**Endpoint:** `POST /procesos-garantia/`

**Cuerpo:**
```json
{
  "ejecucion": 2,
  "garantia": 456,
  "etapa_actual": "PENDIENTE"
}
```

### 2. Avanzar a Siguiente Etapa

**Endpoint:** `POST /procesos-garantia/{id}/avanzar_etapa/`

**Etapas válidas para garantía:**
- `GRABAR_INFO_VEHICULO`
- `GRABAR_INFO_POLIZA`
- `DESAFILIAR_GARANTIA_REPETIDA`

### 3. Otros Endpoints

Los mismos que desembolso:
- `POST /procesos-garantia/{id}/marcar_error/`
- `POST /procesos-garantia/{id}/completar/`
- `GET /procesos-garantia/?ejecucion={id}`

---

## 💡 Ejemplo de Flujo Completo

### Paso 1: Iniciar Ejecución
```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Crear ejecución
response = requests.post(f"{BASE_URL}/ejecuciones/", json={
    "tipo_proceso": "DESEMBOLSO",
    "estado": "EN_PROGRESO",
    "total_registros": 10,
    "descripcion": "ETL Desembolsos - Batch 001"
})
ejecucion = response.json()
ejecucion_id = ejecucion['id']
```

### Paso 2: Procesar Cada Desembolso
```python
# Para cada desembolso en tu fuente de datos
desembolso_id = 123

# Crear proceso de tracking
response = requests.post(f"{BASE_URL}/procesos-desembolso/", json={
    "ejecucion": ejecucion_id,
    "desembolso": desembolso_id,
    "etapa_actual": "PENDIENTE"
})
proceso = response.json()
proceso_id = proceso['id']

# Ejecutar Etapa 1: Grabar cargos fijos
# ... tu lógica aquí ...
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/avanzar_etapa/", json={
    "etapa": "GRABAR_CARGOS_FIJOS",
    "datos_etapa": {"cargos_creados": 2}
})

# Ejecutar Etapa 2: Desembolso
# ... tu lógica aquí ...
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/avanzar_etapa/", json={
    "etapa": "DESEMBOLSO"
})

# Ejecutar Etapa 3: Fraccionar
# ... tu lógica aquí ...
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/avanzar_etapa/", json={
    "etapa": "FRACCIONAR"
})

# Ejecutar Etapa 4: Seleccionar Pago
# ... tu lógica aquí ...
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/avanzar_etapa/", json={
    "etapa": "SELECCIONAR_PAGO"
})

# Ejecutar Etapa 5: Autorizar
# ... tu lógica aquí ...
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/avanzar_etapa/", json={
    "etapa": "AUTORIZAR"
})

# Marcar como completado
requests.post(f"{BASE_URL}/procesos-desembolso/{proceso_id}/completar/")
```

### Paso 3: Finalizar Ejecución
```python
# Ver progreso
response = requests.get(f"{BASE_URL}/ejecuciones/{ejecucion_id}/progreso/")
progreso = response.json()
print(f"Progreso: {progreso['progreso_porcentaje']}%")

# Completar ejecución
requests.post(f"{BASE_URL}/ejecuciones/{ejecucion_id}/completar/")
```

### Paso 4: Retomar Ejecución Fallida
```python
# Verificar si hay ejecuciones pendientes
response = requests.get(f"{BASE_URL}/ejecuciones/pendientes/", 
                       params={"tipo_proceso": "DESEMBOLSO"})
pendientes = response.json()

if pendientes:
    ejecucion_id = pendientes[0]['id']
    print(f"Retomando ejecución {ejecucion_id}")
    
    # Obtener procesos pendientes
    response = requests.get(f"{BASE_URL}/procesos-desembolso/", 
                           params={"ejecucion": ejecucion_id})
    procesos = response.json()['results']
    
    # Procesar solo los que no están completados
    for proceso in procesos:
        if proceso['etapa_actual'] != 'COMPLETADO':
            # Retomar desde la etapa actual
            # ... continuar procesamiento ...
            pass
```

---

## 🔧 Cliente Python Incluido

Hemos creado un cliente Python que facilita el uso de la API. Está en:
```
etl_tracking_client.py
```

**Uso del cliente:**
```python
from etl_tracking_client import ETLTrackingClient

client = ETLTrackingClient("http://localhost:8000/dexter/api")

# Iniciar ejecución
ejecucion_id = client.iniciar_ejecucion_desembolso(total_registros=100)

# Crear proceso
proceso_id = client.crear_proceso_desembolso(ejecucion_id, desembolso_id=123)

# Avanzar etapas
client.avanzar_etapa_desembolso(proceso_id, 'GRABAR_CARGOS_FIJOS')
client.avanzar_etapa_desembolso(proceso_id, 'DESEMBOLSO')
# ... etc

# Completar
client.completar_proceso_desembolso(proceso_id)
client.completar_ejecucion(ejecucion_id)
```

---

## 📈 Monitoreo y Auditoría

### Ver Historial en Django Admin

Accede a: `http://localhost:8000/admin/`

- **Ejecuciones ETL**: Ver todas las ejecuciones con estadísticas
- **Procesos de Desembolso**: Ver estado de cada desembolso procesado
- **Procesos de Garantía**: Ver estado de cada garantía procesada

### Consultar Progreso Programáticamente

```python
# Obtener progreso detallado
progreso = client.obtener_progreso(ejecucion_id)

print(f"Total: {progreso['total_registros']}")
print(f"Procesados: {progreso['registros_procesados']}")
print(f"Exitosos: {progreso['registros_exitosos']}")
print(f"Fallidos: {progreso['registros_fallidos']}")
print(f"Progreso: {progreso['progreso_porcentaje']}%")
print(f"\nDistribución por etapas:")
for etapa, cantidad in progreso['distribucion_etapas'].items():
    print(f"  {etapa}: {cantidad}")
```

---

## ⚠️ Manejo de Errores

### Registrar Errores
```python
try:
    # Tu lógica de procesamiento
    procesar_desembolso(datos)
except Exception as e:
    # Marcar como error y guardar el mensaje
    client.marcar_error_desembolso(proceso_id, str(e))
```

### Reintentar Procesos Fallidos
```python
# Obtener procesos con error
response = requests.get(f"{BASE_URL}/procesos-desembolso/",
                       params={"ejecucion": ejecucion_id, 
                              "etapa_actual": "ERROR"})
procesos_error = response.json()['results']

# Reintentar si no ha superado el límite de intentos
for proceso in procesos_error:
    if proceso['intentos'] < 3:
        # Reintentar desde la última etapa
        # ... lógica de reintento ...
        pass
```

---

## 🎉 Resumen

1. ✅ **Crear ejecución** al iniciar tu ETL
2. ✅ **Crear proceso** para cada registro a procesar
3. ✅ **Avanzar etapas** conforme avanza el procesamiento
4. ✅ **Marcar errores** si algo falla
5. ✅ **Completar procesos** cuando terminan exitosamente
6. ✅ **Completar ejecución** al finalizar todo
7. ✅ **Retomar** desde donde quedó si hubo un fallo

**¡Tu ETL ahora tiene memoria y puede recuperarse de fallos!** 🚀

