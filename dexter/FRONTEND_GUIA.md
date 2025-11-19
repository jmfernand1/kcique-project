# Guía del Frontend de Dexter - Tracking ETL

## Descripción General

El frontend de Dexter proporciona una interfaz visual completa para hacer seguimiento a las ejecuciones de ETL, tanto para procesos de **Desembolso** como de **Garantía**. El diseño sigue la misma línea de UI/UX que la aplicación Adagio, garantizando una experiencia de usuario consistente.

## Características Principales

### 1. Dashboard Principal (`/dexter/`)

El dashboard ofrece una vista general con:

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

### 2. Lista de Ejecuciones (`/dexter/ejecuciones/`)

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

### 3. Detalle de Ejecución (`/dexter/ejecuciones/<id>/`)

Vista detallada que muestra:

#### Información General
- ID y tipo de proceso
- Estado actual
- Fechas de inicio y fin
- Última etapa ejecutada
- Progreso total (% y números)
- Descripción y mensajes de error (si existen)

#### Distribución por Etapas
Tarjetas visuales mostrando cuántos procesos hay en cada etapa:

**Para Desembolsos:**
- Pendiente
- Grabar Cargos Fijos
- Desembolso
- Fraccionar
- Seleccionar Pago
- Autorizar
- Completado
- Error

**Para Garantías:**
- Pendiente
- Grabar Info Vehículo
- Grabar Info Póliza
- Desafiliar Garantía Repetida
- Completado
- Error

#### Listado de Procesos Individuales
Tabla detallada con cada caso individual:

**Para Desembolsos:**
- Referencia del desembolso
- Número de obligación
- Valor del desembolso
- Etapa actual
- Fechas de inicio y última actualización
- Número de intentos
- Estado y errores (modal con detalles)

**Para Garantías:**
- Placa del vehículo
- Número de obligación
- Referencia
- Etapa actual
- Fechas de inicio y última actualización
- Número de intentos
- Estado y errores (modal con detalles)

## Navegación

El menú principal incluye un nuevo dropdown "Dexter" con:
- **Dashboard ETL**: Vista general de estadísticas
- **Ver Ejecuciones**: Lista completa de todas las ejecuciones

## Características de UX/UI

### Diseño Visual
- Tarjetas con colores semánticos:
  - 🔵 Azul (bg-primary): Total de ejecuciones
  - 🟢 Verde (bg-success): Completadas
  - 🔴 Rojo (bg-danger): Fallidas
  - 🟡 Amarillo (bg-warning): Iniciadas
  - ⚫ Gris (bg-secondary): Pausadas
  - ⚪ Blanco con bordes: Información adicional

### Badges de Estado
- Estados visualizados con badges de colores
- Iconos de Font Awesome para mejor comprensión

### Barras de Progreso
- Visualización clara del avance de cada ejecución
- Colores dinámicos según el porcentaje:
  - Verde: 100%
  - Azul: >50%
  - Amarillo: <50%

### Modales de Error
- Visualización detallada de errores sin abandonar la página
- Incluye mensaje de error y datos de la etapa
- Fácil de cerrar y navegar

## Integración con API

Todas las vistas obtienen datos de los modelos de Django:
- `EjecucionETL`: Ejecuciones principales
- `ProcesoDesembolso`: Procesos individuales de desembolso
- `ProcesoGarantia`: Procesos individuales de garantía

Las APIs REST siguen disponibles en `/dexter/api/` para integración programática.

## Uso Típico

1. **Monitoreo general**: Accede al Dashboard para ver el estado general
2. **Revisión específica**: Usa la lista de ejecuciones para encontrar una ejecución específica
3. **Análisis detallado**: Entra al detalle de ejecución para ver cada caso individual
4. **Depuración**: Haz clic en "Ver Error" en casos fallidos para entender qué sucedió

## Template Tags Personalizados

### `format_duration`
Convierte objetos `timedelta` en formato legible:
```django
{{ promedio_ejecucion|format_duration }}
# Resultado: "2d 3h 45m 12s"
```

### `pprint`
Formatea JSON o diccionarios de manera legible:
```django
{{ proceso.datos_etapa|pprint }}
# Resultado: JSON indentado y formateado
```

## Próximos Pasos Recomendados

1. **Filtros adicionales**: Agregar filtros por fecha
2. **Exportación**: Implementar descarga CSV de ejecuciones
3. **Actualización automática**: Implementar WebSockets o polling para actualización en tiempo real
4. **Gráficos**: Agregar visualizaciones de tendencias con Chart.js
5. **Notificaciones**: Sistema de alertas para ejecuciones fallidas

## Rutas Disponibles

```python
# Frontend
/dexter/                          # Dashboard principal
/dexter/ejecuciones/              # Lista de ejecuciones
/dexter/ejecuciones/<id>/         # Detalle de ejecución

# API (sigue disponible)
/dexter/api/ejecuciones/          # API REST de ejecuciones
/dexter/api/procesos-desembolso/  # API REST de procesos de desembolso
/dexter/api/procesos-garantia/    # API REST de procesos de garantía
```

## Compatibilidad

- Bootstrap 5.3
- Font Awesome 5.15
- Django 4.2+
- Compatible con todos los navegadores modernos

