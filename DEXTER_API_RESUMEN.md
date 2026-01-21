# 🎯 API REST Dexter - Documentación Completa

Esta documentación proporciona una guía completa para integrar y utilizar la API REST de Dexter, diseñada para gestionar desembolsos, garantías y procesos ETL.

---

## 📋 Tabla de Contenidos

1. [Información General](#-información-general)
2. [Modelos de Datos](#-modelos-de-datos)
3. [Endpoints Disponibles](#-endpoints-disponibles)
4. [Guía de Inicio Rápido](#-guía-de-inicio-rápido)
5. [Ejemplos CRUD Completos](#-ejemplos-crud-completos)
6. [Sistema de Tracking ETL](#-sistema-de-tracking-etl)
7. [Filtrado, Búsqueda y Ordenamiento](#-filtrado-búsqueda-y-ordenamiento)
8. [Manejo de Errores](#-manejo-de-errores)
9. [Casos de Uso Comunes](#-casos-de-uso-comunes)

---

## 📡 Información General

### URL Base
```
http://localhost:8000/dexter/api/
```

### Formato de Respuesta
Todas las respuestas son en formato JSON.

### Paginación
La API utiliza paginación automática. La respuesta incluye:
```json
{
    "count": 100,
    "next": "http://localhost:8000/dexter/api/desembolsos/?page=2",
    "previous": null,
    "results": [...]
}
```

---

## 🗄️ Modelos de Datos

### Desembolso

Modelo principal para información financiera de desembolsos.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | Auto | Identificador único |
| `referencia` | string(100) | ✅ | Referencia única del desembolso |
| `obligacion` | bigint | ✅ | Número de obligación |
| `id_cliente` | bigint | ✅ | ID del cliente |
| `nit_beneficiario` | bigint | ✅ | NIT del beneficiario |
| `aliado` | string(255) | ✅ | Nombre del aliado |
| `tipo_cta_destino` | string(50) | ✅ | Tipo de cuenta destino |
| `cod_tipo_cuenta_destino` | integer | ✅ | Código tipo cuenta |
| `num_cta_destino` | bigint | ✅ | Número de cuenta destino |
| `banco_destino` | string(100) | ✅ | Nombre del banco destino |
| `cod_banco_destino` | integer | ✅ | Código del banco destino |
| `valor_desembolso` | float | ✅ | Valor del desembolso |
| `numero_tramos` | integer | ✅ | Número de tramos |
| `plazo_tramo_1` | integer | ✅ | Plazo del tramo 1 |
| `tipo_tasa_tramo_1` | string(10) | ✅ | Tipo de tasa tramo 1 (EA, MV, etc.) |
| `tasa_tramo_1` | float | ✅ | Tasa del tramo 1 |
| `amortizacion_tramo_1` | string(10) | ✅ | Tipo de amortización tramo 1 |
| `plazo_tramo_2` | integer | ✅ | Plazo del tramo 2 |
| `tipo_tasa_tramo_2` | string(10) | ✅ | Tipo de tasa tramo 2 |
| `tasa_tramo_2` | float | ✅ | Tasa del tramo 2 |
| `amortizacion_tramo_2` | string(10) | ✅ | Tipo de amortización tramo 2 |
| `dia_pago_cuota` | integer | ❌ | Día de pago de cuota |
| `estado` | string(50) | ❌ | Estado del desembolso |
| `tipo_desembolso` | FK | ❌ | Referencia a TipoDesembolso |
| `observaciones` | JSON | ❌ | Observaciones adicionales |
| `ids_sharepoint` | JSON | ❌ | IDs de SharePoint |

### CargoFijo

Cargos fijos asociados a un desembolso.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | Auto | Identificador único |
| `desembolso` | FK | ✅ | Referencia al desembolso |
| `codigo` | string(10) | ✅ | Código del cargo |
| `nombre_cargo_fijo` | string(255) | ✅ | Nombre del cargo |
| `fecha_efectiva` | date | ❌ | Fecha efectiva |
| `fecha_revision` | date | ❌ | Fecha de revisión |
| `periodicidad` | string(50) | ❌ | Periodicidad (MENSUAL, ANUAL, etc.) |
| `valor` | float | ❌ | Valor del cargo |

### Garantia

Información de garantías vehiculares.

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `id` | integer | Auto | Identificador único |
| `referencia` | string(100) | ❌ | Referencia |
| `obligacion` | bigint | ✅ | Número de obligación |
| `id_cliente` | bigint | ✅ | ID del cliente |
| `id_garante` | bigint | ✅ | ID del garante |
| `cod_fasecolda` | string(50) | ✅ | Código Fasecolda |
| `codigo_fasecolda` | string(50) | ✅ | Código Fasecolda (alternativo) |
| `color` | string(100) | ❌ | Color del vehículo |
| `placa` | string(20) | ✅ | Placa del vehículo |
| `poliza_vehiculo` | string(50) | ❌ | Póliza del vehículo |
| `cod_aseguradora` | string(20) | ❌ | Código de aseguradora |
| `nro_poliza` | string(50) | ❌ | Número de póliza |
| `valor_asegurado` | float | ❌ | Valor asegurado |
| `fecha_vencimiento_seguro` | date | ❌ | Vencimiento del seguro |
| `tipo_prima` | string(50) | ❌ | Tipo de prima |
| `valor_prima` | float | ❌ | Valor de la prima |
| `folio_electronico` | string(50) | ❌ | Folio electrónico |
| `valor_vehiculo` | bigint | ❌ | Valor del vehículo |
| `modelo` | string(10) | ❌ | Modelo (año) |
| `fecha_prenda` | date | ❌ | Fecha de prenda |
| `chasis` | string(50) | ❌ | Número de chasis |
| `motor` | string(50) | ❌ | Número de motor |
| `serie` | string(50) | ❌ | Número de serie |
| `servicio` | string(50) | ❌ | Tipo de servicio |
| `fecha_desembolso` | date | ❌ | Fecha de desembolso |
| `estado` | string(50) | ❌ | Estado de la garantía |

---

## 🔗 Endpoints Disponibles

### Endpoints de Datos Principales

#### Desembolsos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/desembolsos/` | Listar todos los desembolsos |
| POST | `/api/desembolsos/` | Crear un nuevo desembolso |
| GET | `/api/desembolsos/{id}/` | Obtener un desembolso específico |
| PUT | `/api/desembolsos/{id}/` | Actualizar completamente un desembolso |
| PATCH | `/api/desembolsos/{id}/` | Actualizar parcialmente un desembolso |
| DELETE | `/api/desembolsos/{id}/` | Eliminar un desembolso |
| GET | `/api/desembolsos/{id}/cargos_fijos/` | Obtener cargos fijos del desembolso |

#### Cargos Fijos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/cargos-fijos/` | Listar todos los cargos fijos |
| POST | `/api/cargos-fijos/` | Crear un nuevo cargo fijo |
| GET | `/api/cargos-fijos/{id}/` | Obtener un cargo fijo específico |
| PUT | `/api/cargos-fijos/{id}/` | Actualizar completamente un cargo fijo |
| PATCH | `/api/cargos-fijos/{id}/` | Actualizar parcialmente un cargo fijo |
| DELETE | `/api/cargos-fijos/{id}/` | Eliminar un cargo fijo |

#### Garantías
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/garantias/` | Listar todas las garantías |
| POST | `/api/garantias/` | Crear una nueva garantía |
| GET | `/api/garantias/{id}/` | Obtener una garantía específica |
| PUT | `/api/garantias/{id}/` | Actualizar completamente una garantía |
| PATCH | `/api/garantias/{id}/` | Actualizar parcialmente una garantía |
| DELETE | `/api/garantias/{id}/` | Eliminar una garantía |

### Endpoints de Tracking ETL

#### Ejecuciones ETL
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/ejecuciones/` | Listar todas las ejecuciones |
| POST | `/api/ejecuciones/` | Crear nueva ejecución |
| GET | `/api/ejecuciones/{id}/` | Obtener una ejecución |
| PATCH | `/api/ejecuciones/{id}/` | Actualizar ejecución |
| POST | `/api/ejecuciones/crear_con_plan/` | Crear ejecución con plan completo |
| GET | `/api/ejecuciones/pendientes/` | Obtener ejecuciones pendientes |
| POST | `/api/ejecuciones/{id}/retomar/` | Retomar ejecución pausada |
| POST | `/api/ejecuciones/{id}/completar/` | Marcar como completada |
| POST | `/api/ejecuciones/{id}/fallar/` | Marcar como fallida |
| GET | `/api/ejecuciones/{id}/progreso/` | Obtener progreso detallado |

#### Procesos de Desembolso
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/procesos-desembolso/` | Listar procesos |
| GET | `/api/procesos-desembolso/{id}/` | Obtener proceso |
| GET | `/api/procesos-desembolso/{id}/siguiente_etapa/` | Obtener siguiente etapa |

#### Etapas de Proceso Desembolso
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/etapas-proceso-desembolso/` | Listar etapas |
| GET | `/api/etapas-proceso-desembolso/{id}/` | Obtener etapa |
| POST | `/api/etapas-proceso-desembolso/{id}/iniciar/` | Iniciar etapa |
| POST | `/api/etapas-proceso-desembolso/{id}/completar/` | Completar etapa |
| POST | `/api/etapas-proceso-desembolso/{id}/marcar_error/` | Marcar error |
| POST | `/api/etapas-proceso-desembolso/{id}/reintentar/` | Reintentar etapa |

#### Configuración de Tipos
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET/POST | `/api/tipos-desembolso/` | Gestionar tipos de desembolso |
| GET | `/api/tipos-desembolso/{id}/etapas/` | Obtener etapas de un tipo |
| GET/POST | `/api/tipos-garantia/` | Gestionar tipos de garantía |
| GET/POST | `/api/etapas-desembolso/` | Gestionar etapas de tipo desembolso |
| GET/POST | `/api/etapas-garantia/` | Gestionar etapas de tipo garantía |

---

## 🚀 Guía de Inicio Rápido

### Requisitos Previos
```bash
pip install requests
```

### Cliente Python Básico

```python
import requests
from typing import Optional, Dict, Any, List

class DexterAPIClient:
    """Cliente para la API REST de Dexter"""
    
    def __init__(self, base_url: str = "http://localhost:8000/dexter/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Realiza una petición a la API"""
        url = f"{self.base_url}/{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        if response.status_code == 204:
            return {}
        return response.json()
    
    # ==================== DESEMBOLSOS ====================
    
    def listar_desembolsos(self, **params) -> Dict:
        """Lista todos los desembolsos con filtros opcionales"""
        return self._request("GET", "desembolsos/", params=params)
    
    def obtener_desembolso(self, desembolso_id: int) -> Dict:
        """Obtiene un desembolso por ID"""
        return self._request("GET", f"desembolsos/{desembolso_id}/")
    
    def crear_desembolso(self, datos: Dict) -> Dict:
        """Crea un nuevo desembolso"""
        return self._request("POST", "desembolsos/", json=datos)
    
    def actualizar_desembolso(self, desembolso_id: int, datos: Dict) -> Dict:
        """Actualiza un desembolso completamente"""
        return self._request("PUT", f"desembolsos/{desembolso_id}/", json=datos)
    
    def actualizar_parcial_desembolso(self, desembolso_id: int, datos: Dict) -> Dict:
        """Actualiza parcialmente un desembolso"""
        return self._request("PATCH", f"desembolsos/{desembolso_id}/", json=datos)
    
    def eliminar_desembolso(self, desembolso_id: int) -> None:
        """Elimina un desembolso"""
        self._request("DELETE", f"desembolsos/{desembolso_id}/")
    
    def obtener_cargos_desembolso(self, desembolso_id: int) -> List[Dict]:
        """Obtiene los cargos fijos de un desembolso"""
        return self._request("GET", f"desembolsos/{desembolso_id}/cargos_fijos/")
    
    # ==================== CARGOS FIJOS ====================
    
    def crear_cargo_fijo(self, datos: Dict) -> Dict:
        """Crea un nuevo cargo fijo"""
        return self._request("POST", "cargos-fijos/", json=datos)
    
    def listar_cargos_fijos(self, **params) -> Dict:
        """Lista todos los cargos fijos"""
        return self._request("GET", "cargos-fijos/", params=params)
    
    # ==================== GARANTÍAS ====================
    
    def listar_garantias(self, **params) -> Dict:
        """Lista todas las garantías"""
        return self._request("GET", "garantias/", params=params)
    
    def obtener_garantia(self, garantia_id: int) -> Dict:
        """Obtiene una garantía por ID"""
        return self._request("GET", f"garantias/{garantia_id}/")
    
    def crear_garantia(self, datos: Dict) -> Dict:
        """Crea una nueva garantía"""
        return self._request("POST", "garantias/", json=datos)
    
    def actualizar_garantia(self, garantia_id: int, datos: Dict) -> Dict:
        """Actualiza una garantía completamente"""
        return self._request("PUT", f"garantias/{garantia_id}/", json=datos)
    
    def eliminar_garantia(self, garantia_id: int) -> None:
        """Elimina una garantía"""
        self._request("DELETE", f"garantias/{garantia_id}/")


# Uso del cliente
if __name__ == "__main__":
    client = DexterAPIClient()
    
    # Listar desembolsos
    resultado = client.listar_desembolsos()
    print(f"Total desembolsos: {resultado['count']}")
```

---

## 📝 Ejemplos CRUD Completos

### 1. Crear un Desembolso

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Datos del desembolso
datos_desembolso = {
    "referencia": "DES-2026-001",
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
    "observaciones": {"nota": "Desembolso de prueba"}
}

# Crear desembolso
response = requests.post(
    f"{BASE_URL}/desembolsos/",
    json=datos_desembolso
)

if response.status_code == 201:
    desembolso = response.json()
    print(f"✅ Desembolso creado con ID: {desembolso['id']}")
    print(f"   Referencia: {desembolso['referencia']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
```

### 2. Obtener un Desembolso con sus Cargos Fijos

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"
desembolso_id = 1

# Obtener desembolso (incluye cargos_fijos automáticamente)
response = requests.get(f"{BASE_URL}/desembolsos/{desembolso_id}/")

if response.status_code == 200:
    desembolso = response.json()
    print(f"📋 Desembolso: {desembolso['referencia']}")
    print(f"   Valor: ${desembolso['valor_desembolso']:,.2f}")
    print(f"   Aliado: {desembolso['aliado']}")
    
    # Los cargos fijos vienen incluidos en la respuesta
    if desembolso.get('cargos_fijos'):
        print(f"\n📌 Cargos Fijos ({len(desembolso['cargos_fijos'])}):")
        for cargo in desembolso['cargos_fijos']:
            print(f"   - {cargo['nombre_cargo_fijo']}: ${cargo['valor']:,.2f}")
else:
    print(f"❌ Error: {response.status_code}")
```

### 3. Crear un Cargo Fijo para un Desembolso

```python
import requests
from datetime import date

BASE_URL = "http://localhost:8000/dexter/api"

# Datos del cargo fijo
datos_cargo = {
    "desembolso": 1,  # ID del desembolso
    "codigo": "ADM001",
    "nombre_cargo_fijo": "Cuota de Administración",
    "fecha_efectiva": date.today().isoformat(),
    "periodicidad": "MENSUAL",
    "valor": 25000.00
}

response = requests.post(
    f"{BASE_URL}/cargos-fijos/",
    json=datos_cargo
)

if response.status_code == 201:
    cargo = response.json()
    print(f"✅ Cargo fijo creado con ID: {cargo['id']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
```

### 4. Actualización Parcial (PATCH)

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"
desembolso_id = 1

# Solo actualizar los campos necesarios
datos_parciales = {
    "estado": "APROBADO",
    "observaciones": {
        "nota": "Desembolso aprobado",
        "fecha_aprobacion": "2026-01-21"
    }
}

response = requests.patch(
    f"{BASE_URL}/desembolsos/{desembolso_id}/",
    json=datos_parciales
)

if response.status_code == 200:
    desembolso = response.json()
    print(f"✅ Desembolso actualizado")
    print(f"   Nuevo estado: {desembolso['estado']}")
else:
    print(f"❌ Error: {response.status_code}")
```

### 5. Crear una Garantía

```python
import requests
from datetime import date

BASE_URL = "http://localhost:8000/dexter/api"

datos_garantia = {
    "referencia": "GAR-2026-001",
    "obligacion": 123456789,
    "id_cliente": 987654321,
    "id_garante": 123456,
    "cod_fasecolda": "001234",
    "codigo_fasecolda": "001234",
    "color": "Blanco",
    "placa": "ABC123",
    "valor_vehiculo": 50000000,
    "modelo": "2024",
    "chasis": "CHASIS123456789",
    "motor": "MOTOR123456",
    "servicio": "PARTICULAR",
    "poliza_vehiculo": "POL-001",
    "cod_aseguradora": "ASG01",
    "nro_poliza": "123456",
    "valor_asegurado": 45000000.00,
    "fecha_vencimiento_seguro": "2027-01-21",
    "tipo_prima": "ANUAL",
    "valor_prima": 1500000.00,
    "fecha_desembolso": date.today().isoformat(),
    "estado": "ACTIVA"
}

response = requests.post(
    f"{BASE_URL}/garantias/",
    json=datos_garantia
)

if response.status_code == 201:
    garantia = response.json()
    print(f"✅ Garantía creada con ID: {garantia['id']}")
    print(f"   Placa: {garantia['placa']}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.json())
```

### 6. Eliminar Registros

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Eliminar un desembolso
desembolso_id = 1
response = requests.delete(f"{BASE_URL}/desembolsos/{desembolso_id}/")

if response.status_code == 204:
    print(f"✅ Desembolso {desembolso_id} eliminado correctamente")
else:
    print(f"❌ Error: {response.status_code}")
```

---

## 🔄 Sistema de Tracking ETL

El sistema de tracking ETL permite gestionar ejecuciones de procesos masivos con seguimiento de progreso por etapas.

### Arquitectura del Sistema

```
EjecucionETL (Contenedor principal)
    └── ProcesoDesembolso / ProcesoGarantia (Por cada registro)
            └── EtapaProcesoDesembolso / EtapaProcesoGarantia (Por cada etapa)
```

### Estados Disponibles

**Ejecución ETL:**
- `INICIADO` - Ejecución creada
- `EN_PROGRESO` - Procesando registros
- `COMPLETADO` - Todos los registros procesados
- `FALLIDO` - Error durante la ejecución
- `PAUSADO` - Ejecución pausada manualmente

**Proceso/Etapa:**
- `PENDIENTE` - No iniciado
- `EN_PROGRESO` - En proceso
- `COMPLETADO` - Finalizado exitosamente
- `ERROR` - Error durante el proceso
- `OMITIDA` - Etapa omitida

### Ejemplo Completo: Flujo ETL de Desembolsos

```python
import requests
from datetime import date
from time import sleep

BASE_URL = "http://localhost:8000/dexter/api"

class ETLTrackingClient:
    """Cliente para el sistema de tracking ETL"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def crear_tipo_desembolso(self, nombre: str, etapas: list) -> dict:
        """Crea un tipo de desembolso con sus etapas"""
        # Crear tipo de desembolso
        tipo = self.session.post(
            f"{self.base_url}/tipos-desembolso/",
            json={"nombre": nombre, "descripcion": f"Proceso de {nombre}"}
        ).json()
        
        # Crear etapas
        for i, etapa_nombre in enumerate(etapas, 1):
            self.session.post(
                f"{self.base_url}/etapas-desembolso/",
                json={
                    "nombre": etapa_nombre,
                    "descripcion": f"Etapa: {etapa_nombre}",
                    "orden": i,
                    "tipo_desembolso": tipo["id"]
                }
            )
        
        return tipo
    
    def crear_ejecucion_con_plan(
        self, 
        tipo_proceso: str, 
        desembolso_ids: list = None,
        garantia_ids: list = None,
        descripcion: str = None
    ) -> dict:
        """Crea una ejecución ETL con su plan completo"""
        data = {
            "tipo_proceso": tipo_proceso,
            "total_registros": len(desembolso_ids or garantia_ids or []),
            "descripcion": descripcion
        }
        
        if tipo_proceso == "DESEMBOLSO" and desembolso_ids:
            data["desembolso_ids"] = desembolso_ids
        elif tipo_proceso == "GARANTIA" and garantia_ids:
            data["garantia_ids"] = garantia_ids
        
        response = self.session.post(
            f"{self.base_url}/ejecuciones/crear_con_plan/",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def obtener_progreso(self, ejecucion_id: int) -> dict:
        """Obtiene el progreso detallado de una ejecución"""
        response = self.session.get(
            f"{self.base_url}/ejecuciones/{ejecucion_id}/progreso/"
        )
        return response.json()
    
    def obtener_procesos_pendientes(self, ejecucion_id: int) -> list:
        """Obtiene los procesos pendientes de una ejecución"""
        response = self.session.get(
            f"{self.base_url}/procesos-desembolso/",
            params={"ejecucion": ejecucion_id}
        )
        return response.json().get("results", [])
    
    def obtener_siguiente_etapa(self, proceso_id: int) -> dict:
        """Obtiene la siguiente etapa de un proceso"""
        response = self.session.get(
            f"{self.base_url}/procesos-desembolso/{proceso_id}/siguiente_etapa/"
        )
        if response.status_code == 204:
            return None
        return response.json()
    
    def iniciar_etapa(self, etapa_id: int) -> dict:
        """Inicia una etapa"""
        response = self.session.post(
            f"{self.base_url}/etapas-proceso-desembolso/{etapa_id}/iniciar/"
        )
        return response.json()
    
    def completar_etapa(self, etapa_id: int, datos_etapa: dict = None) -> dict:
        """Completa una etapa con datos opcionales"""
        data = {}
        if datos_etapa:
            data["datos_etapa"] = datos_etapa
        
        response = self.session.post(
            f"{self.base_url}/etapas-proceso-desembolso/{etapa_id}/completar/",
            json=data
        )
        return response.json()
    
    def marcar_error_etapa(self, etapa_id: int, mensaje: str, datos: dict = None) -> dict:
        """Marca una etapa como error"""
        data = {"mensaje_error": mensaje}
        if datos:
            data["datos_etapa"] = datos
        
        response = self.session.post(
            f"{self.base_url}/etapas-proceso-desembolso/{etapa_id}/marcar_error/",
            json=data
        )
        return response.json()
    
    def reintentar_etapa(self, etapa_id: int) -> dict:
        """Reintenta una etapa fallida"""
        response = self.session.post(
            f"{self.base_url}/etapas-proceso-desembolso/{etapa_id}/reintentar/"
        )
        return response.json()
    
    def completar_ejecucion(self, ejecucion_id: int) -> dict:
        """Marca una ejecución como completada"""
        response = self.session.post(
            f"{self.base_url}/ejecuciones/{ejecucion_id}/completar/"
        )
        return response.json()


# =============================================================================
# EJEMPLO DE USO COMPLETO
# =============================================================================

def ejemplo_flujo_etl_completo():
    """Ejemplo completo de un flujo ETL con tracking"""
    
    client = ETLTrackingClient()
    
    # PASO 1: Configurar tipo de desembolso con etapas
    print("📝 Configurando tipo de desembolso...")
    tipo = client.crear_tipo_desembolso(
        nombre="Desembolso Estándar",
        etapas=[
            "Validación de Datos",
            "Verificación de Cliente",
            "Aprobación Financiera",
            "Transferencia Bancaria",
            "Notificación"
        ]
    )
    print(f"   ✅ Tipo creado: {tipo['nombre']} (ID: {tipo['id']})")
    
    # PASO 2: Crear desembolsos de prueba
    print("\n📝 Creando desembolsos de prueba...")
    desembolso_ids = []
    for i in range(3):
        response = requests.post(
            f"{BASE_URL}/desembolsos/",
            json={
                "referencia": f"ETL-TEST-{i+1}",
                "obligacion": 100000000 + i,
                "id_cliente": 200000000 + i,
                "nit_beneficiario": 900000000 + i,
                "aliado": "ALIADO_TEST",
                "tipo_cta_destino": "Ahorros",
                "cod_tipo_cuenta_destino": 1,
                "num_cta_destino": 1234567890 + i,
                "banco_destino": "Banco Test",
                "cod_banco_destino": 51,
                "valor_desembolso": 5000000 * (i + 1),
                "numero_tramos": 1,
                "plazo_tramo_1": 12,
                "tipo_tasa_tramo_1": "EA",
                "tasa_tramo_1": 15.0,
                "amortizacion_tramo_1": "FRANCESA",
                "plazo_tramo_2": 0,
                "tipo_tasa_tramo_2": "EA",
                "tasa_tramo_2": 0,
                "amortizacion_tramo_2": "FRANCESA",
                "tipo_desembolso": tipo['id']
            }
        )
        desembolso = response.json()
        desembolso_ids.append(desembolso['id'])
        print(f"   ✅ Desembolso creado: {desembolso['referencia']}")
    
    # PASO 3: Crear ejecución ETL con plan
    print("\n🚀 Creando ejecución ETL...")
    ejecucion = client.crear_ejecucion_con_plan(
        tipo_proceso="DESEMBOLSO",
        desembolso_ids=desembolso_ids,
        descripcion="ETL de prueba - Procesamiento de 3 desembolsos"
    )
    print(f"   ✅ Ejecución creada ID: {ejecucion['id']}")
    print(f"   Estado: {ejecucion['estado']}")
    print(f"   Total registros: {ejecucion['total_registros']}")
    
    # PASO 4: Procesar cada registro
    print("\n⚙️ Procesando registros...")
    procesos = client.obtener_procesos_pendientes(ejecucion['id'])
    
    for proceso in procesos:
        print(f"\n📦 Procesando: {proceso['desembolso_referencia']}")
        
        # Procesar cada etapa del proceso
        while True:
            etapa = client.obtener_siguiente_etapa(proceso['id'])
            if not etapa:
                print(f"   ✅ Todas las etapas completadas")
                break
            
            print(f"   ▶️ Etapa: {etapa['etapa_nombre']}")
            
            # Iniciar etapa
            client.iniciar_etapa(etapa['id'])
            
            # Simular procesamiento
            sleep(0.5)
            
            # Completar etapa con datos
            client.completar_etapa(
                etapa['id'],
                datos_etapa={
                    "resultado": "exitoso",
                    "timestamp": date.today().isoformat()
                }
            )
            print(f"      ✅ Completada")
    
    # PASO 5: Finalizar ejecución
    print("\n🏁 Finalizando ejecución...")
    ejecucion_final = client.completar_ejecucion(ejecucion['id'])
    print(f"   Estado final: {ejecucion_final['estado']}")
    
    # PASO 6: Mostrar resumen
    progreso = client.obtener_progreso(ejecucion['id'])
    print(f"\n📊 RESUMEN DE EJECUCIÓN:")
    print(f"   - Total registros: {progreso['total_registros']}")
    print(f"   - Procesados: {progreso['registros_procesados']}")
    print(f"   - Exitosos: {progreso['registros_exitosos']}")
    print(f"   - Fallidos: {progreso['registros_fallidos']}")
    print(f"   - Progreso: {progreso['progreso_porcentaje']}%")


if __name__ == "__main__":
    ejemplo_flujo_etl_completo()
```

### Manejo de Errores en ETL

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

def procesar_con_manejo_errores(etapa_id: int):
    """Ejemplo de procesamiento con manejo de errores"""
    
    # Iniciar etapa
    requests.post(f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/iniciar/")
    
    try:
        # Simular procesamiento que puede fallar
        resultado = realizar_operacion_externa()
        
        # Si todo sale bien, completar
        requests.post(
            f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/completar/",
            json={"datos_etapa": {"resultado": resultado}}
        )
        
    except Exception as e:
        # Si falla, marcar error
        requests.post(
            f"{BASE_URL}/etapas-proceso-desembolso/{etapa_id}/marcar_error/",
            json={
                "mensaje_error": str(e),
                "datos_etapa": {"traceback": "..."}
            }
        )


def reintentar_etapas_fallidas(ejecucion_id: int):
    """Reintenta todas las etapas fallidas de una ejecución"""
    
    # Obtener etapas en error
    response = requests.get(
        f"{BASE_URL}/etapas-proceso-desembolso/",
        params={
            "proceso__ejecucion": ejecucion_id,
            "estado": "ERROR"
        }
    )
    
    etapas_error = response.json().get("results", [])
    
    for etapa in etapas_error:
        print(f"Reintentando etapa {etapa['id']}: {etapa['etapa_nombre']}")
        
        # Reintentar
        response = requests.post(
            f"{BASE_URL}/etapas-proceso-desembolso/{etapa['id']}/reintentar/"
        )
        
        if response.status_code == 200:
            # La etapa está nuevamente EN_PROGRESO
            procesar_con_manejo_errores(etapa['id'])
```

---

## 🔍 Filtrado, Búsqueda y Ordenamiento

### Filtrado por Campos Exactos

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Filtrar desembolsos por aliado
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"aliado": "ALIADO_PRUEBA"}
)

# Filtrar por múltiples campos
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={
        "aliado": "ALIADO_PRUEBA",
        "nit_beneficiario": 900123456
    }
)

# Filtrar garantías por placa
response = requests.get(
    f"{BASE_URL}/garantias/",
    params={"placa": "ABC123"}
)

# Filtrar cargos fijos por desembolso
response = requests.get(
    f"{BASE_URL}/cargos-fijos/",
    params={"desembolso": 1}
)

# Filtrar ejecuciones por tipo y estado
response = requests.get(
    f"{BASE_URL}/ejecuciones/",
    params={
        "tipo_proceso": "DESEMBOLSO",
        "estado": "EN_PROGRESO"
    }
)
```

### Campos de Filtrado Disponibles

| Endpoint | Campos de Filtrado |
|----------|-------------------|
| `/desembolsos/` | `referencia`, `obligacion`, `id_cliente`, `nit_beneficiario`, `aliado` |
| `/cargos-fijos/` | `desembolso`, `codigo`, `periodicidad` |
| `/garantias/` | `referencia`, `obligacion`, `id_cliente`, `id_garante`, `placa`, `cod_fasecolda`, `cod_aseguradora` |
| `/ejecuciones/` | `tipo_proceso`, `estado` |
| `/procesos-desembolso/` | `ejecucion`, `estado_general`, `desembolso` |
| `/etapas-proceso-desembolso/` | `proceso`, `etapa`, `estado` |

### Búsqueda Full-Text

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Buscar en desembolsos (busca en: referencia, aliado, banco_destino)
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"search": "Banco Popular"}
)

# Buscar en garantías (busca en: referencia, placa, chasis, motor, nro_poliza)
response = requests.get(
    f"{BASE_URL}/garantias/",
    params={"search": "ABC"}
)

# Buscar en cargos fijos (busca en: nombre_cargo_fijo, codigo)
response = requests.get(
    f"{BASE_URL}/cargos-fijos/",
    params={"search": "administración"}
)
```

### Ordenamiento

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Ordenar ascendente por valor
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"ordering": "valor_desembolso"}
)

# Ordenar descendente (usar signo -)
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"ordering": "-valor_desembolso"}
)

# Ordenar por múltiples campos
response = requests.get(
    f"{BASE_URL}/garantias/",
    params={"ordering": "placa,-valor_vehiculo"}
)
```

### Campos de Ordenamiento Disponibles

| Endpoint | Campos de Ordenamiento |
|----------|----------------------|
| `/desembolsos/` | `id`, `referencia`, `valor_desembolso` |
| `/cargos-fijos/` | `id`, `fecha_efectiva`, `valor` |
| `/garantias/` | `id`, `placa`, `fecha_desembolso`, `valor_vehiculo` |

### Paginación

```python
import requests

BASE_URL = "http://localhost:8000/dexter/api"

# Primera página (por defecto)
response = requests.get(f"{BASE_URL}/desembolsos/")
data = response.json()

print(f"Total registros: {data['count']}")
print(f"Siguiente página: {data['next']}")
print(f"Página anterior: {data['previous']}")
print(f"Registros en esta página: {len(data['results'])}")

# Página específica
response = requests.get(
    f"{BASE_URL}/desembolsos/",
    params={"page": 2}
)

# Iterar todas las páginas
def obtener_todos_los_registros(endpoint: str) -> list:
    """Obtiene todos los registros paginados"""
    todos = []
    url = f"{BASE_URL}/{endpoint}/"
    
    while url:
        response = requests.get(url)
        data = response.json()
        todos.extend(data['results'])
        url = data['next']
    
    return todos

# Uso
todos_los_desembolsos = obtener_todos_los_registros("desembolsos")
```

---

## ⚠️ Manejo de Errores

### Códigos de Estado HTTP

| Código | Significado |
|--------|-------------|
| `200` | Éxito - Solicitud procesada correctamente |
| `201` | Creado - Recurso creado exitosamente |
| `204` | Sin contenido - Eliminación exitosa |
| `400` | Error de solicitud - Datos inválidos |
| `404` | No encontrado - Recurso no existe |
| `500` | Error del servidor |

### Manejo de Errores en Python

```python
import requests
from requests.exceptions import RequestException, HTTPError

BASE_URL = "http://localhost:8000/dexter/api"

def crear_desembolso_seguro(datos: dict) -> dict:
    """Crea un desembolso con manejo robusto de errores"""
    
    try:
        response = requests.post(
            f"{BASE_URL}/desembolsos/",
            json=datos,
            timeout=30  # Timeout de 30 segundos
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
        
    except HTTPError as e:
        # Error HTTP (4xx, 5xx)
        error_detail = {}
        try:
            error_detail = e.response.json()
        except:
            error_detail = {"detail": str(e)}
        
        return {
            "success": False,
            "status_code": e.response.status_code,
            "error": error_detail
        }
        
    except RequestException as e:
        # Error de conexión, timeout, etc.
        return {
            "success": False,
            "error": {"detail": f"Error de conexión: {str(e)}"}
        }


# Uso
resultado = crear_desembolso_seguro({
    "referencia": "TEST-001",
    # ... otros campos
})

if resultado["success"]:
    print(f"✅ Desembolso creado: {resultado['data']['id']}")
else:
    print(f"❌ Error: {resultado['error']}")
```

### Errores Comunes y Soluciones

```python
# ERROR: Campo requerido faltante
# Respuesta: {"referencia": ["This field is required."]}
# Solución: Asegurar que todos los campos requeridos estén presentes

# ERROR: Referencia duplicada
# Respuesta: {"referencia": ["desembolso with this referencia already exists."]}
# Solución: Usar una referencia única

# ERROR: Tipo de dato incorrecto
# Respuesta: {"valor_desembolso": ["A valid number is required."]}
# Solución: Verificar los tipos de datos

# ERROR: Recurso no encontrado
# Respuesta: {"detail": "Not found."}
# Solución: Verificar que el ID existe
```

---

## 💡 Casos de Uso Comunes

### 1. Carga Masiva desde CSV

```python
import requests
import pandas as pd
from typing import List, Dict

BASE_URL = "http://localhost:8000/dexter/api"

def cargar_desembolsos_desde_csv(archivo_csv: str) -> Dict[str, List]:
    """Carga desembolsos desde un archivo CSV"""
    
    df = pd.read_csv(archivo_csv)
    resultados = {"exitosos": [], "fallidos": []}
    
    for index, row in df.iterrows():
        datos = {
            "referencia": row['referencia'],
            "obligacion": int(row['obligacion']),
            "id_cliente": int(row['id_cliente']),
            "nit_beneficiario": int(row['nit_beneficiario']),
            "aliado": row['aliado'],
            "tipo_cta_destino": row['tipo_cta_destino'],
            "cod_tipo_cuenta_destino": int(row['cod_tipo_cuenta_destino']),
            "num_cta_destino": int(row['num_cta_destino']),
            "banco_destino": row['banco_destino'],
            "cod_banco_destino": int(row['cod_banco_destino']),
            "valor_desembolso": float(row['valor_desembolso']),
            "numero_tramos": int(row['numero_tramos']),
            "plazo_tramo_1": int(row['plazo_tramo_1']),
            "tipo_tasa_tramo_1": row['tipo_tasa_tramo_1'],
            "tasa_tramo_1": float(row['tasa_tramo_1']),
            "amortizacion_tramo_1": row['amortizacion_tramo_1'],
            "plazo_tramo_2": int(row.get('plazo_tramo_2', 0)),
            "tipo_tasa_tramo_2": row.get('tipo_tasa_tramo_2', 'EA'),
            "tasa_tramo_2": float(row.get('tasa_tramo_2', 0)),
            "amortizacion_tramo_2": row.get('amortizacion_tramo_2', 'FRANCESA')
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/desembolsos/",
                json=datos
            )
            response.raise_for_status()
            resultados["exitosos"].append(row['referencia'])
            print(f"✅ {row['referencia']}")
        except Exception as e:
            resultados["fallidos"].append({
                "referencia": row['referencia'],
                "error": str(e)
            })
            print(f"❌ {row['referencia']}: {e}")
    
    return resultados


# Uso
resultados = cargar_desembolsos_desde_csv("desembolsos.csv")
print(f"\nResumen: {len(resultados['exitosos'])} exitosos, {len(resultados['fallidos'])} fallidos")
```

### 2. Sincronización Bidireccional

```python
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000/dexter/api"

def sincronizar_desembolso(referencia: str, datos_externos: dict) -> dict:
    """Sincroniza un desembolso: crea si no existe, actualiza si existe"""
    
    # Buscar si existe
    response = requests.get(
        f"{BASE_URL}/desembolsos/",
        params={"referencia": referencia}
    )
    
    existentes = response.json()["results"]
    
    if existentes:
        # Existe - actualizar
        desembolso_id = existentes[0]["id"]
        response = requests.patch(
            f"{BASE_URL}/desembolsos/{desembolso_id}/",
            json=datos_externos
        )
        accion = "actualizado"
    else:
        # No existe - crear
        datos_externos["referencia"] = referencia
        response = requests.post(
            f"{BASE_URL}/desembolsos/",
            json=datos_externos
        )
        accion = "creado"
    
    response.raise_for_status()
    return {"accion": accion, "data": response.json()}
```

### 3. Reporte de Estado de Ejecuciones

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/dexter/api"

def generar_reporte_ejecuciones() -> dict:
    """Genera un reporte de estado de todas las ejecuciones"""
    
    response = requests.get(f"{BASE_URL}/ejecuciones/")
    ejecuciones = response.json()["results"]
    
    reporte = {
        "total": len(ejecuciones),
        "por_estado": {},
        "por_tipo": {},
        "detalle": []
    }
    
    for ej in ejecuciones:
        # Contar por estado
        estado = ej["estado"]
        reporte["por_estado"][estado] = reporte["por_estado"].get(estado, 0) + 1
        
        # Contar por tipo
        tipo = ej["tipo_proceso"]
        reporte["por_tipo"][tipo] = reporte["por_tipo"].get(tipo, 0) + 1
        
        # Obtener progreso detallado
        progreso = requests.get(
            f"{BASE_URL}/ejecuciones/{ej['id']}/progreso/"
        ).json()
        
        reporte["detalle"].append({
            "id": ej["id"],
            "tipo": tipo,
            "estado": estado,
            "progreso": f"{progreso['progreso_porcentaje']}%",
            "exitosos": progreso["registros_exitosos"],
            "fallidos": progreso["registros_fallidos"]
        })
    
    return reporte


# Uso
reporte = generar_reporte_ejecuciones()
print(f"📊 REPORTE DE EJECUCIONES")
print(f"Total: {reporte['total']}")
print(f"Por estado: {reporte['por_estado']}")
print(f"Por tipo: {reporte['por_tipo']}")
```

### 4. Exportar Datos a DataFrame (Pandas)

```python
import requests
import pandas as pd

BASE_URL = "http://localhost:8000/dexter/api"

def exportar_desembolsos_a_dataframe() -> pd.DataFrame:
    """Exporta todos los desembolsos a un DataFrame de Pandas"""
    
    todos_los_registros = []
    url = f"{BASE_URL}/desembolsos/"
    
    while url:
        response = requests.get(url)
        data = response.json()
        todos_los_registros.extend(data["results"])
        url = data["next"]
    
    df = pd.DataFrame(todos_los_registros)
    return df


def exportar_garantias_a_dataframe() -> pd.DataFrame:
    """Exporta todas las garantías a un DataFrame de Pandas"""
    
    todos_los_registros = []
    url = f"{BASE_URL}/garantias/"
    
    while url:
        response = requests.get(url)
        data = response.json()
        todos_los_registros.extend(data["results"])
        url = data["next"]
    
    df = pd.DataFrame(todos_los_registros)
    return df


# Uso
df_desembolsos = exportar_desembolsos_a_dataframe()
print(df_desembolsos.head())

# Guardar a Excel
df_desembolsos.to_excel("desembolsos_export.xlsx", index=False)

# Análisis básico
print(f"\nTotal desembolsos: {len(df_desembolsos)}")
print(f"Valor total: ${df_desembolsos['valor_desembolso'].sum():,.2f}")
print(f"Por aliado:\n{df_desembolsos.groupby('aliado')['valor_desembolso'].sum()}")
```

---

## 🧪 Verificación del Sistema

```bash
# Verificar que no hay problemas en la configuración
python manage.py check

# Verificar migraciones
python manage.py showmigrations dexter

# Iniciar servidor
python manage.py runserver

# Probar en navegador
# Navega a: http://localhost:8000/dexter/api/
```

---

## 📁 Estructura de Archivos

```
dexter/
├── __init__.py
├── admin.py                  # Configuración del admin de Django
├── apps.py                   # Configuración de la app
├── forms.py                  # Formularios para vistas web
├── models.py                 # Modelos: Desembolso, CargoFijo, Garantia, ETL
├── serializers.py            # Serializers para la API REST
├── services.py               # Lógica de negocio para tracking ETL
├── viewsets.py               # ViewSets para la API REST
├── views.py                  # Vistas web (templates)
├── urls.py                   # Configuración de URLs y router
├── tests.py                  # Tests (por implementar)
├── README.md                 # Documentación detallada
└── migrations/
    ├── __init__.py
    └── 0001_initial.py       # Migración inicial
```

---

## 🎉 Resumen

La API **Dexter** ofrece:

1. **CRUD Completo**: Todas las operaciones para Desembolsos, Cargos Fijos y Garantías
2. **Sistema de Tracking ETL**: Gestión de ejecuciones masivas con seguimiento por etapas
3. **Filtrado Avanzado**: Filtros por múltiples campos
4. **Búsqueda Full-Text**: Búsqueda en campos de texto
5. **Ordenamiento**: Ordenar por múltiples campos
6. **Paginación**: Respuestas paginadas
7. **Manejo de Errores**: Control de etapas fallidas y reintentos

**Para comenzar:**
1. Inicia el servidor: `python manage.py runserver`
2. Abre en el navegador: http://localhost:8000/dexter/api/
3. Usa los ejemplos de esta documentación para integrar tu aplicación

¡La API está lista para recibir datos de tu ETL! 🚀
