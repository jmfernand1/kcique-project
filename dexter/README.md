# Dexter - Sistema Completo de ETL y Tracking

## 📋 Descripción

**Dexter** es una aplicación Django completa que proporciona:
- 🎨 **Frontend Web**: Interfaz visual moderna para monitoreo y seguimiento de procesos ETL
- 🔌 **API REST**: API completa para la gestión programática de desembolsos, cargos fijos y garantías
- 📊 **Sistema de Tracking**: Seguimiento detallado de cada ejecución ETL con visibilidad de etapas individuales

Diseñada para integrarse perfectamente con procesos ETL (Extract, Transform, Load) en Python, permitiendo tanto la operación manual como automatizada.

## 🎨 Frontend Web - Interfaz Visual

### Acceso Rápido
- **Dashboard Principal**: http://localhost:8000/dexter/
- **Lista de Ejecuciones**: http://localhost:8000/dexter/ejecuciones/

### Características del Frontend

#### 📊 Dashboard Principal
- Vista general con estadísticas en tiempo real
- Tarjetas de métricas por estado (Completadas, En Progreso, Fallidas, etc.)
- Estadísticas por tipo de proceso (Desembolsos vs Garantías)
- Tiempo promedio de ejecución
- Tabla de ejecuciones recientes con barras de progreso

#### 📋 Lista de Ejecuciones
- Filtros avanzados por tipo de proceso, estado y búsqueda
- Paginación inteligente (20 registros por página)
- Visualización clara del progreso de cada ejecución
- Información detallada de registros procesados, exitosos y fallidos

#### 🔍 Detalle de Ejecución
La vista más completa que incluye:

**Información General:**
- Estado actual y fechas de inicio/fin
- Métricas de progreso visual
- Descripción y mensajes de error

**Distribución por Etapas:**
- Tarjetas visuales por cada etapa del proceso
- Contador de casos en cada etapa
- Códigos de color según el estado

**Procesos Individuales:**
- Tabla detallada de cada caso (desembolso o garantía)
- Etapa actual de cada proceso
- Modales emergentes con detalles de errores
- Número de intentos y fechas de actualización

### Características de UX/UI

✅ **Diseño consistente** con la aplicación Adagio
✅ **Responsive** - funciona en desktop y móvil
✅ **Barras de progreso** animadas
✅ **Badges de color** para estados
✅ **Modales** para información detallada
✅ **Iconos Font Awesome** para mejor comprensión
✅ **Filtros en tiempo real** sin recargar página

### Datos de Prueba

Para poblar el sistema con datos de prueba y visualizar el frontend:

```bash
# En el shell de Django
python manage.py shell

# Ejecutar:
from dexter.crear_datos_prueba import crear_datos_prueba
crear_datos_prueba()
```

Esto creará:
- 15 desembolsos de ejemplo
- 10 garantías de ejemplo
- 5 ejecuciones ETL en diferentes estados
- Procesos individuales en diversas etapas

### Documentación del Frontend

Para documentación detallada del frontend, consulta:
- `FRONTEND_GUIA.md` - Guía completa de uso
- `crear_datos_prueba.py` - Script para generar datos de prueba

## 🗄️ Modelos de Datos

### Modelos de Tracking ETL

#### EjecucionETL
Registra cada ejecución completa del ETL con:
- Tipo de proceso (DESEMBOLSO o GARANTIA)
- Estado (INICIADO, EN_PROGRESO, COMPLETADO, FALLIDO, PAUSADO)
- Contadores de registros totales, procesados, exitosos y fallidos
- Fechas de inicio y fin
- Última etapa ejecutada y mensajes de error

#### ProcesoDesembolso
Tracking individual de cada desembolso en el ETL con etapas:
1. PENDIENTE
2. GRABAR_CARGOS_FIJOS
3. DESEMBOLSO
4. FRACCIONAR
5. SELECCIONAR_PAGO
6. AUTORIZAR
7. COMPLETADO / ERROR

#### ProcesoGarantia
Tracking individual de cada garantía en el ETL con etapas:
1. PENDIENTE
2. GRABAR_INFO_VEHICULO
3. GRABAR_INFO_POLIZA
4. DESAFILIAR_GARANTIA_REPETIDA
5. COMPLETADO / ERROR

### Modelos de Datos Principales

#### 1. Desembolso
Modelo principal que almacena información de desembolsos financieros.

**Campos principales:**
- `referencia` - Referencia única del desembolso
- `obligacion` - Número de obligación
- `id_cliente` - ID del cliente
- `nit_beneficiario` - NIT del beneficiario
- `aliado` - Nombre del aliado comercial
- `valor_desembolso` - Valor del desembolso
- `numero_tramos` - Número de tramos (1 o 2)
- Información de cuenta destino
- Información de tramos (plazo, tasa, amortización)

#### 2. CargoFijo
Cargos fijos asociados a un desembolso (relación ForeignKey).

**Campos principales:**
- `desembolso` - Relación con Desembolso
- `codigo` - Código del cargo
- `nombre_cargo_fijo` - Nombre descriptivo
- `fecha_efectiva` - Fecha de efectividad
- `periodicidad` - Frecuencia del cargo
- `valor` - Valor del cargo

#### 3. Garantía
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

## 🔌 Endpoints de la API

### URL Base
```
http://localhost:8000/dexter/api/
```

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

## 🚀 Uso desde Python (ETL)

### Instalación de dependencias
```bash
pip install requests
```

### Ejemplo básico

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Crear un desembolso
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
    "amortizacion_tramo_2": "FRANCESA"
}

response = requests.post(f"{BASE_URL}/desembolsos/", json=datos)
desembolso = response.json()
print(f"Desembolso creado con ID: {desembolso['id']}")

# Listar desembolsos
response = requests.get(f"{BASE_URL}/desembolsos/")
desembolsos = response.json()
print(f"Total de desembolsos: {desembolsos['count']}")

# Filtrar por aliado
response = requests.get(f"{BASE_URL}/desembolsos/", params={'aliado': 'ALIADO_PRUEBA'})
desembolsos_filtrados = response.json()

# Actualizar un desembolso
datos_actualizar = {"valor_desembolso": 12000000.00}
response = requests.patch(f"{BASE_URL}/desembolsos/1/", json=datos_actualizar)
```

### Cliente completo

Para un cliente completo con todas las funcionalidades, consulta el archivo `ejemplo_uso_api.py` incluido en esta aplicación.

## 🛠️ Configuración

### 1. Migraciones
```bash
python manage.py makemigrations dexter
python manage.py migrate dexter
```

### 2. Iniciar el servidor
```bash
python manage.py runserver
```

### 3. Acceder a la API
- API navegable: http://localhost:8000/dexter/api/
- Admin de Django: http://localhost:8000/admin/

## 📊 Características de la API

### Paginación
La API está paginada por defecto (10 elementos por página). Puedes navegar usando:
```
GET /desembolsos/?page=2
```

### Filtros
Usa parámetros de query para filtrar:
```
GET /desembolsos/?aliado=ALIADO_PRUEBA&estado=ACTIVO
```

### Búsqueda
Usa el parámetro `search` para buscar:
```
GET /desembolsos/?search=ABC123
```

### Ordenamiento
Usa el parámetro `ordering` para ordenar:
```
GET /desembolsos/?ordering=-valor_desembolso  # Descendente
GET /desembolsos/?ordering=referencia          # Ascendente
```

## 🔐 Autenticación (Opcional)

Si necesitas agregar autenticación a la API, puedes configurar Django Rest Framework con tokens o JWT:

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

## 📝 Notas Importantes

1. **Referencia única**: El campo `referencia` en Desembolso debe ser único
2. **Relaciones**: Al eliminar un Desembolso, se eliminan automáticamente sus CargosFijos (CASCADE)
3. **Campos opcionales**: Muchos campos son opcionales (`null=True, blank=True`) para flexibilidad
4. **Validación**: La API valida automáticamente los datos según los modelos

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

## 📞 Soporte

Para más información sobre Django Rest Framework:
- [Documentación oficial](https://www.django-rest-framework.org/)
- [Tutorial de DRF](https://www.django-rest-framework.org/tutorial/quickstart/)

## 📄 Licencia

Este proyecto es parte del sistema Kcique.

