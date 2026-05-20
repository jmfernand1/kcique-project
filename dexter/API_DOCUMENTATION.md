# Documentación de la API — App `dexter`

Guía para desarrolladores que necesiten **consumir** o **entregar información** a la
integración Dexter (ETL de Desembolsos y Garantías + tracking de procesos).

---

## 1. Información general

| Concepto            | Valor                                                          |
|---------------------|----------------------------------------------------------------|
| Framework           | Django REST Framework (DRF) — `ModelViewSet` + `DefaultRouter`  |
| URL base            | `http://<host>:<puerto>/dexter/api/`                            |
| Ejemplo local       | `http://localhost:8000/dexter/api/`                             |
| Formato de datos    | JSON (`Content-Type: application/json`)                         |
| Autenticación       | Actualmente **abierta** (sin token). Ver sección 7.             |
| Paginación          | Activada — las listas devuelven `count`, `next`, `previous`, `results` |
| Esquema OpenAPI 3   | Generado con `drf-spectacular`. Ver sección 11.                 |

> Todos los recursos exponen el CRUD estándar salvo que se indique lo contrario.

### Operaciones estándar (aplican a cada recurso `<recurso>`)

| Método | Ruta                       | Descripción                       |
|--------|----------------------------|-----------------------------------|
| GET    | `/<recurso>/`              | Listar (paginado, filtrable)      |
| POST   | `/<recurso>/`              | Crear                             |
| GET    | `/<recurso>/{id}/`         | Obtener un registro               |
| PUT    | `/<recurso>/{id}/`         | Reemplazar (todos los campos)     |
| PATCH  | `/<recurso>/{id}/`         | Actualizar parcialmente           |
| DELETE | `/<recurso>/{id}/`         | Eliminar                          |

---

## 2. Catálogo de endpoints

### Endpoints de datos (negocio)

| Recurso        | Ruta base               | Modelo      |
|----------------|-------------------------|-------------|
| Desembolsos    | `/dexter/api/desembolsos/`  | `Desembolso` |
| Cargos fijos   | `/dexter/api/cargos-fijos/` | `CargoFijo`  |
| Garantías      | `/dexter/api/garantias/`    | `Garantia`   |

### Endpoints de tracking ETL

| Recurso                  | Ruta base                              |
|--------------------------|----------------------------------------|
| Ejecuciones ETL          | `/dexter/api/ejecuciones/`             |
| Procesos de desembolso   | `/dexter/api/procesos-desembolso/`     |
| Procesos de garantía     | `/dexter/api/procesos-garantia/`       |
| Etapas proceso desembolso| `/dexter/api/etapas-proceso-desembolso/` |
| Etapas proceso garantía  | `/dexter/api/etapas-proceso-garantia/` |
| Tipos de desembolso      | `/dexter/api/tipos-desembolso/`        |
| Tipos de garantía        | `/dexter/api/tipos-garantia/`          |
| Etapas tipo desembolso   | `/dexter/api/etapas-desembolso/`       |
| Etapas tipo garantía     | `/dexter/api/etapas-garantia/`         |

---

## 3. Formato de fechas (¡importante!)

Los campos de fecha de **Desembolso/CargoFijo/Garantía** usan el formato `YYYYMMDD`.

- **Al enviar** (POST/PUT/PATCH) se acepta:
  - Entero: `20260131`
  - Texto: `"20260131"`
  - Texto ISO: `"2026-01-31"`
- **Al recibir** (GET) la API devuelve siempre un **entero** `YYYYMMDD` (ej. `20260131`).

Campos afectados: `CargoFijo.fecha_efectiva`, `CargoFijo.fecha_revision`,
`Garantia.fecha_desembolso`, `Garantia.fecha_prenda`, `Garantia.fecha_vencimiento_seguro`.

Errores típicos: `"Formato inválido. Use YYYYMMDD (8 dígitos)."`,
`"Fecha inexistente (revise día/mes)."`

---

## 4. Modelos / payloads

### 4.1 Desembolso — `POST /dexter/api/desembolsos/`

| Campo                   | Tipo     | Requerido | Notas                              |
|-------------------------|----------|-----------|------------------------------------|
| `referencia`            | string   | Sí        | Único                              |
| `obligacion`            | int      | Sí        |                                    |
| `id_cliente`            | int      | Sí        |                                    |
| `nit_beneficiario`      | int      | Sí        |                                    |
| `aliado`                | string   | Sí        | máx. 255                           |
| `tipo_cta_destino`      | string   | Sí        | máx. 50                            |
| `cod_tipo_cuenta_destino`| int     | Sí        |                                    |
| `num_cta_destino`       | int      | No        |                                    |
| `banco_destino`         | string   | No        |                                    |
| `cod_banco_destino`     | int      | No        |                                    |
| `valor_desembolso`      | float    | Sí        |                                    |
| `numero_tramos`         | int      | Sí        |                                    |
| `dia_pago_cuota`        | int      | No        |                                    |
| `estado`                | string   | No        |                                    |
| `tipo_desembolso`       | int (FK) | No        | id de `TipoDesembolso`             |
| `observaciones`         | objeto   | No        | JSON libre                         |
| `ids_sharepoint`        | objeto   | No        | JSON libre                         |
| `etapa_desembolso`      | int      | No        | default `0`                        |
| `intentos_desembolso`   | int      | No        | default `0`                        |

> En **lectura** (`GET`) el desembolso incluye su lista anidada `cargos_fijos`.
> En **escritura** los cargos fijos NO se anidan: se crean aparte vía `/cargos-fijos/`.

```json
{
  "referencia": "DES-001",
  "obligacion": 9001234567,
  "id_cliente": 1234567,
  "nit_beneficiario": 8001234561,
  "aliado": "Aliado XYZ",
  "tipo_cta_destino": "AHORROS",
  "cod_tipo_cuenta_destino": 1,
  "num_cta_destino": 123456789,
  "banco_destino": "Bancolombia",
  "cod_banco_destino": 7,
  "valor_desembolso": 15000000.0,
  "numero_tramos": 1,
  "dia_pago_cuota": 5,
  "tipo_desembolso": 1
}
```

### 4.2 CargoFijo — `POST /dexter/api/cargos-fijos/`

| Campo               | Tipo     | Requerido | Notas                    |
|---------------------|----------|-----------|--------------------------|
| `desembolso`        | int (FK) | Sí        | id de `Desembolso`       |
| `codigo`            | string   | Sí        | máx. 10                  |
| `nombre_cargo_fijo` | string   | Sí        | máx. 255                 |
| `fecha_efectiva`    | YYYYMMDD | No        | ver sección 3            |
| `fecha_revision`    | YYYYMMDD | No        | ver sección 3            |
| `periodicidad`      | string   | No        |                          |
| `valor`             | float    | No        |                          |

```json
{
  "desembolso": 10,
  "codigo": "CF01",
  "nombre_cargo_fijo": "Cuota de manejo",
  "fecha_efectiva": 20260131,
  "fecha_revision": "2026-06-30",
  "periodicidad": "MENSUAL",
  "valor": 12000.0
}
```

### 4.3 Garantía — `POST /dexter/api/garantias/`

| Campo                     | Tipo     | Requerido | Notas             |
|---------------------------|----------|-----------|-------------------|
| `referencia`              | string   | Sí        | Único             |
| `obligacion`              | int      | Sí        |                   |
| `id_cliente`              | int      | Sí        |                   |
| `id_garante`              | int      | Sí        |                   |
| `cod_fasecolda`           | string   | Sí        |                   |
| `codigo_fasecolda`        | string   | Sí        |                   |
| `placa`                   | string   | Sí        | máx. 20           |
| `color`                   | string   | No        |                   |
| `poliza_vehiculo`         | string   | No        |                   |
| `cod_aseguradora`         | string   | No        |                   |
| `nro_poliza`              | string   | No        |                   |
| `valor_asegurado`         | float    | No        |                   |
| `fecha_vencimiento_seguro`| YYYYMMDD | No        | ver sección 3     |
| `tipo_prima`              | string   | No        |                   |
| `valor_prima`             | float    | No        |                   |
| `folio_electronico`       | string   | No        |                   |
| `valor_vehiculo`          | int      | No        |                   |
| `modelo`                  | string   | No        |                   |
| `fecha_prenda`            | YYYYMMDD | No        | ver sección 3     |
| `chasis` `motor` `serie` `servicio` | string | No |               |
| `fecha_desembolso`        | YYYYMMDD | No        | ver sección 3     |
| `estado`                  | string   | No        |                   |

### 4.4 EjecucionETL

| Campo                  | Tipo   | Notas                                              |
|------------------------|--------|----------------------------------------------------|
| `tipo_proceso`         | string | `DESEMBOLSO` \| `GARANTIA`                         |
| `estado`               | string | `INICIADO`,`EN_PROGRESO`,`COMPLETADO`,`FALLIDO`,`PAUSADO` (default `INICIADO`) |
| `total_registros`      | int    |                                                    |
| `registros_procesados` | int    |                                                    |
| `registros_exitosos`   | int    |                                                    |
| `registros_fallidos`   | int    |                                                    |
| `descripcion`          | string |                                                    |
| `mensaje_error`        | string |                                                    |
| `fecha_inicio`/`fecha_fin` | datetime | Solo lectura                                  |
| `progreso`             | float  | Solo lectura — % calculado                         |

### 4.5 Estados de procesos y etapas

- `ProcesoDesembolso` / `ProcesoGarantia` → `estado_general`:
  `PENDIENTE`, `EN_PROGRESO`, `COMPLETADO`, `ERROR`, `PAUSADO`.
- `EtapaProcesoDesembolso` / `EtapaProcesoGarantia` → `estado`:
  `PENDIENTE`, `EN_PROGRESO`, `COMPLETADO`, `ERROR`, `OMITIDA`.
  Incluyen `datos_etapa` (JSON), `mensaje_error`, `intentos`, `orden`.

---

## 5. Endpoints personalizados (acciones)

| Método | Ruta                                              | Descripción / Body |
|--------|---------------------------------------------------|--------------------|
| GET    | `/desembolsos/{id}/cargos_fijos/`                 | Cargos fijos del desembolso |
| POST   | `/ejecuciones/crear_con_plan/`                    | Crea ejecución + plan (ver abajo) |
| GET    | `/ejecuciones/pendientes/?tipo_proceso=DESEMBOLSO`| Ejecuciones no completadas |
| POST   | `/ejecuciones/{id}/retomar/`                      | Reanuda una ejecución |
| POST   | `/ejecuciones/{id}/completar/`                    | Marca como completada |
| POST   | `/ejecuciones/{id}/fallar/`                       | Body: `{"mensaje_error": "..."}` |
| GET    | `/ejecuciones/{id}/progreso/`                     | Progreso detallado |
| GET    | `/procesos-desembolso/{id}/siguiente_etapa/`      | Siguiente etapa pendiente (`204` si no hay) |
| GET    | `/procesos-garantia/{id}/siguiente_etapa/`        | Igual para garantías |
| GET    | `/tipos-desembolso/{id}/etapas/`                  | Etapas configuradas del tipo |
| POST   | `/etapas-proceso-desembolso/{id}/iniciar/`        | Inicia la etapa |
| POST   | `/etapas-proceso-desembolso/{id}/completar/`      | Body: `{"datos_etapa": {...}}` |
| POST   | `/etapas-proceso-desembolso/{id}/marcar_error/`   | Body: `{"mensaje_error": "...", "datos_etapa": {...}}` |
| POST   | `/etapas-proceso-desembolso/{id}/reintentar/`     | Reintenta la etapa |
| POST   | `/etapas-proceso-garantia/{id}/iniciar\|completar\|marcar_error\|reintentar/` | Idéntico para garantías |

### Body de `POST /ejecuciones/crear_con_plan/`

```json
{
  "tipo_proceso": "DESEMBOLSO",
  "total_registros": 100,
  "descripcion": "ETL Desembolsos - Batch 001",
  "desembolso_ids": [1, 2, 3]
}
```
Si `tipo_proceso` es `GARANTIA`, enviar `garantia_ids` en lugar de `desembolso_ids`.
Respuesta: `201 Created` con la ejecución y sus procesos generados.

---

## 6. Filtros, búsqueda y orden (query params)

Aplican sobre los endpoints de listado (`GET /<recurso>/`).

| Recurso              | `?campo=` (filtro exacto)                                              | `?search=` | `?ordering=` |
|----------------------|------------------------------------------------------------------------|------------|--------------|
| desembolsos          | `referencia`,`obligacion`,`id_cliente`,`nit_beneficiario`,`aliado`,`estado` | referencia, aliado, banco_destino | id, referencia, valor_desembolso |
| cargos-fijos         | `desembolso`,`codigo`,`periodicidad`                                   | nombre_cargo_fijo, codigo | id, fecha_efectiva, valor |
| garantias            | `referencia`,`obligacion`,`id_cliente`,`id_garante`,`placa`,`cod_fasecolda`,`cod_aseguradora`,`estado` | referencia, placa, chasis, motor, nro_poliza | id, placa, fecha_desembolso, valor_vehiculo |
| ejecuciones          | `tipo_proceso`,`estado`                                                | —          | fecha_inicio |
| procesos-desembolso  | `ejecucion`,`estado_general`,`desembolso`                              | —          | fecha_creacion |
| procesos-garantia    | `ejecucion`,`estado_general`,`garantia`                                | —          | fecha_creacion |
| etapas-proceso-*     | `proceso`,`etapa`,`estado`                                             | —          | orden |

Ejemplo: `GET /dexter/api/desembolsos/?estado=PENDIENTE&search=XYZ&ordering=-valor_desembolso`

---

## 7. Autenticación

Hoy la API está **abierta** (sin token). Para habilitar autenticación por token en
`settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
}
```
Con ello cada petición deberá enviar la cabecera:
`Authorization: Token <tu_token>`

---

## 8. Códigos de respuesta

| Código | Significado                                                       |
|--------|-------------------------------------------------------------------|
| 200    | OK (GET / PUT / PATCH / acciones de éxito)                        |
| 201    | Creado (POST)                                                     |
| 204    | Sin contenido (DELETE, o `siguiente_etapa` sin etapas pendientes) |
| 400    | Error de validación / negocio → `{"error": "..."}` o `{"campo": ["..."]}` |
| 404    | Recurso no encontrado → `{"error": "... no encontrado"}`          |

---

## 9. Ejemplo de consumo (Python `requests`)

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# 1. Crear un desembolso
desembolso = requests.post(f"{BASE_URL}/desembolsos/", json={
    "referencia": "DES-001", "obligacion": 9001234567, "id_cliente": 1234567,
    "nit_beneficiario": 8001234561, "aliado": "Aliado XYZ",
    "tipo_cta_destino": "AHORROS", "cod_tipo_cuenta_destino": 1,
    "valor_desembolso": 15000000.0, "numero_tramos": 1,
}).json()

# 2. Agregar un cargo fijo
requests.post(f"{BASE_URL}/cargos-fijos/", json={
    "desembolso": desembolso["id"], "codigo": "CF01",
    "nombre_cargo_fijo": "Cuota de manejo", "fecha_efectiva": 20260131,
    "valor": 12000.0,
})

# 3. Crear la ejecución ETL con su plan
ejecucion = requests.post(f"{BASE_URL}/ejecuciones/crear_con_plan/", json={
    "tipo_proceso": "DESEMBOLSO", "total_registros": 1,
    "descripcion": "ETL Batch 001", "desembolso_ids": [desembolso["id"]],
}).json()

# 4. Procesar etapa por etapa
procesos = requests.get(f"{BASE_URL}/procesos-desembolso/",
                        params={"ejecucion": ejecucion["id"]}).json()["results"]
for proc in procesos:
    etapa = requests.get(
        f"{BASE_URL}/procesos-desembolso/{proc['id']}/siguiente_etapa/").json()
    requests.post(f"{BASE_URL}/etapas-proceso-desembolso/{etapa['id']}/iniciar/")
    requests.post(f"{BASE_URL}/etapas-proceso-desembolso/{etapa['id']}/completar/",
                  json={"datos_etapa": {"resultado": "ok"}})
```

> Scripts de referencia en el repo: `ejemplo_uso_api.py`,
> `ejemplo_tracking_desembolsos.py`, `ejemplo_tracking_garantias.py`.

---

## 10. Cómo entregar la información al equipo de integración

1. Identifica el recurso: datos de negocio (`desembolsos`, `cargos-fijos`,
   `garantias`) o tracking (`ejecuciones`, `procesos-*`, `etapas-*`).
2. Arma el JSON respetando **campos requeridos** (sección 4) y el **formato de
   fecha `YYYYMMDD`** (sección 3).
3. Cada `Desembolso`/`Garantía` necesita una `referencia` **única**; los
   `CargoFijo` se asocian por el `id` del desembolso.
4. Para procesar un lote: crea los registros → llama `crear_con_plan/` → recorre
   las etapas con `iniciar/` y `completar/` (o `marcar_error/`).
5. Entrega al equipo: URL base del ambiente, el/los JSON de ejemplo y el token de
   autenticación si el ambiente lo exige (sección 7).

---

## 11. Esquema OpenAPI 3 / Swagger (drf-spectacular)

La API publica su esquema **OpenAPI 3** de forma automática mediante
`drf-spectacular`. El esquema solo incluye los endpoints de Dexter.

### Endpoints de documentación

| Ruta                            | Descripción                                      |
|---------------------------------|--------------------------------------------------|
| `/api/schema/`                  | Descarga el esquema en **`.yaml`** (OpenAPI 3)   |
| `/api/schema/?format=json`      | Descarga el esquema en **`.json`**               |
| `/api/docs/`                    | UI interactiva **Swagger** (probar endpoints)    |
| `/api/redoc/`                   | UI alternativa **ReDoc** (lectura)               |

Ejemplo local: `http://localhost:8000/api/docs/`

### Descargar el esquema `.yaml`

**Opción A — desde el navegador / cliente HTTP:**
```
GET http://localhost:8000/api/schema/
```
La respuesta es el archivo `schema.yaml` listo para importar en Postman,
Insomnia, Swagger Editor, generadores de clientes (`openapi-generator`), etc.

**Opción B — por línea de comandos (sin levantar el servidor):**
```bash
python manage.py spectacular --file dexter/schema.yaml
```

El esquema versionado en el repositorio está en
[`dexter/schema.yaml`](./schema.yaml) y se debe regenerar con el comando
anterior cada vez que cambien modelos, serializers o viewsets.

### Configuración (ya aplicada en el proyecto)

- `drf_spectacular` agregado a `INSTALLED_APPS`.
- `REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'`.
- Bloque `SPECTACULAR_SETTINGS` en `kcique_project/settings.py`.
- Rutas `schema/docs/redoc` en `kcique_project/urls.py`.
- Hook `dexter/schema_hooks.py` que filtra el esquema a solo `/dexter/api/`.
- Dependencia `drf-spectacular==0.29.0` en `requirements.txt`.
