# Kcique - Kiosco Centralizador de Informes y Queries

## 📋 Descripción del Proyecto

**Kcique** es una plataforma web desarrollada en Django diseñada para centralizar y optimizar automatizaciones y la gestión de información crítica en el sector financiero. Se enfoca especialmente en el Monitoreo e Inteligencia de Originación y Cobranzas, proporcionando herramientas para:

- **Gestión de Procesos Automatizados**: Centralización, ejecución y monitoreo de scripts Python
- **Programación de Tareas**: Sistema de cron integrado para automatizar procesos
- **Gestión de Casos de Débito**: Sistema especializado para el manejo de casos bancarios
- **API REST**: Endpoints para integración con otros sistemas
- **Dashboard Inteligente**: Visualización de métricas y estado de procesos

### 🏗️ Arquitectura del Sistema

El proyecto está compuesto por dos aplicaciones principales:

1. **Automations**: Gestión de procesos automatizados y programación de tareas
2. **Adagio**: Gestión especializada de casos de débito bancario

## 🛠️ Requisitos del Sistema

### Requisitos de Software

- **Python**: 3.8 o superior
- **Django**: 5.0.6
- **Base de datos**: SQLite (incluida) o PostgreSQL/MySQL para producción
- **Sistema operativo**: Windows, macOS o Linux

### Dependencias Python

```bash
Django==5.0.6
djangorestframework==3.15.1
django-filter==24.2
django-crispy-forms==2.1
crispy-bootstrap5==2024.2
django-q2==1.8.0
numpy==2.2.6
pandas==2.3.0
python-dateutil==2.9.0.post0
pytz==2025.2
```

## 🚀 Instalación Paso a Paso

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd kcique_project
```

### 2. Crear Entorno Virtual

```bash
# En Windows
python -m venv venv
venv\Scripts\activate

# En macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la Base de Datos

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 6. Configurar Archivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 7. Iniciar el Servidor de Desarrollo

```bash
python manage.py runserver
```

El sistema estará disponible en: `http://localhost:8000`

## ⚙️ Configuración Inicial

### 1. Configuración de Django-Q (Procesamiento en Background)

Django-Q maneja las tareas programadas y procesamiento en segundo plano. Para iniciarlo:

```bash
# En una nueva terminal (con el entorno virtual activado)
python manage.py qcluster
```

### 2. Configuración de Zona Horaria

El sistema está configurado para **Colombia (America/Bogota)**. Para cambiar:

```python
# En kcique_project/settings.py
TIME_ZONE = 'America/Bogota'  # Cambiar según necesidad
```

### 3. Configuración de Producción

Para entornos de producción, modifique:

```python
# En kcique_project/settings.py
DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'tu-ip']

# Configurar base de datos de producción
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tu_bd',
        'USER': 'tu_usuario',
        'PASSWORD': 'tu_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 📚 Guía de Usuario

### 🏠 Página Principal

Al acceder al sistema, encontrará:

1. **Bienvenida**: Descripción general del sistema
2. **Navegación principal**: Acceso a todas las funcionalidades
3. **Acceso rápido**: Botón directo a automatizaciones

### 🤖 Módulo de Automatizaciones

#### Crear un Proceso Automatizado

1. **Navegue a**: Automatizaciones → Ver Procesos
2. **Haga clic en**: "Crear Nuevo Proceso"
3. **Complete los campos**:
   - **Nombre**: Identificador único del proceso
   - **Descripción**: Explicación detallada del propósito
   - **Ruta del Script**: Ruta absoluta al archivo Python
   - **Entorno Virtual**: (Opcional) Ruta al venv específico
   - **Activo**: Marcar para habilitar ejecución

4. **Ejemplo de configuración**:
   ```
   Nombre: Procesar Archivos Diarios
   Descripción: Script que procesa archivos CSV del día anterior
   Ruta del Script: /home/usuario/scripts/procesar_archivos.py
   Entorno Virtual: /home/usuario/venvs/mi_env
   ```

#### Ejecutar un Proceso

**Ejecución Manual**:
1. Vaya a la lista de procesos
2. Haga clic en el proceso deseado
3. Presione "Ejecutar Proceso"
4. Monitoree el progreso en la sección de logs

**Ejecución Programada**:
1. **Navegue a**: Automatizaciones → Programar Tareas
2. **Haga clic en**: "Nueva Tarea Programada"
3. **Configure la programación**:
   - **Proceso**: Seleccione el proceso a automatizar
   - **Frecuencia**: Elija entre:
     - Cada X Minutos/Horas
     - Diario (especifique hora)
     - Semanal (día y hora)
     - Mensual (día del mes y hora)
     - Una sola vez (fecha específica)

4. **Ejemplos de programación**:
   ```
   Diario a las 06:00 AM:
   - Frecuencia: Diario
   - Hora: 06:00

   Cada 30 minutos:
   - Frecuencia: Cada X Minutos
   - Intervalo: 30

   Lunes a las 08:00 AM:
   - Frecuencia: Semanal
   - Día: Lunes
   - Hora: 08:00
   ```

#### Monitorear Procesos

**Estado del Clúster**:
- **Navegue a**: Automatizaciones → Estado del Clúster
- **Visualice**: Estado de Django-Q, tareas activas, estadísticas

**Logs de Ejecución**:
1. Haga clic en cualquier proceso
2. Revise la sección "Logs Recientes"
3. Vea estado: INICIADO, CORRIENDO, EXITOSO, FALLIDO

### ⚡ Módulo Adagio (Casos de Débito)

#### Dashboard de Casos

**Navegue a**: Adagio → Dashboard

**Métricas disponibles**:
- Casos pendientes por estado
- Total de casos procesados
- Tiempo promedio de ejecución
- Casos recientes

#### Cargar Casos desde CSV

1. **Vaya al Dashboard de Adagio**
2. **En la sección "Cargar Datos"**:
   - Seleccione archivo CSV
   - Haga clic en "Cargar Archivo"

3. **Formato del CSV requerido**:
   ```csv
   cod_caso_bizagi,num_prestamo,docsoldv,doctitulardv,tipo_de_cuenta,numcta_debito,secuencia_cta,codigo_del_banco,codigo_ciudad,tipo_debito,autoriza,fecha_desembolso,estado
   CASO001,12345,DOC123,1234567890,AHORROS,9876543210,001,001,001,AL TITULAR,AUTO,2024-01-15,PENDIENTE
   ```

4. **Campos obligatorios**:
   - `cod_caso_bizagi`: Código único del caso

5. **Estados disponibles**:
   - PENDIENTE
   - GRABADO
   - PENDIENTE BIZAGI
   - FINALIZADO
   - VALIDAR
   - CON ERROR

#### Gestionar Casos Individuales

**Ver lista de casos**:
1. **Navegue a**: Adagio → Ver Casos
2. **Funcionalidades**:
   - Búsqueda por código, préstamo, documento
   - Filtros por estado
   - Paginación automática

**Crear caso manual**:
1. Haga clic en "Nuevo Caso"
2. Complete los campos requeridos
3. Guarde el caso

**Editar caso existente**:
1. Haga clic en el caso deseado
2. Seleccione "Editar"
3. Modifique los campos necesarios
4. Guarde cambios

### 🔧 Script de Carga Automática

El sistema incluye un script Python para carga masiva de casos:

```bash
# Ubicar archivo CSV en la raíz del proyecto como "casos_pendientes.csv"
python scripts/cargar_casos.py
```

**Configuración del script**:
- Modifique `ruta_del_csv` en el script según su necesidad
- El script maneja creación y actualización automática de casos
- Proporciona resumen detallado de la operación

## 🌐 API REST

### Endpoints Disponibles

#### Casos de Débito API

**URL Base**: `/adagio/api/`

**Endpoints**:
```
GET    /adagio/api/casos/           # Listar todos los casos
POST   /adagio/api/casos/           # Crear nuevo caso
GET    /adagio/api/casos/{id}/      # Obtener caso específico
PUT    /adagio/api/casos/{id}/      # Actualizar caso completo
PATCH  /adagio/api/casos/{id}/      # Actualizar campos específicos
DELETE /adagio/api/casos/{id}/      # Eliminar caso
```

**Filtros disponibles**:
```
GET /adagio/api/casos/?estado=PENDIENTE
GET /adagio/api/casos/?cod_caso_bizagi=CASO001
GET /adagio/api/casos/?num_prestamo=12345
```

**Ejemplo de uso con cURL**:
```bash
# Obtener todos los casos pendientes
curl -X GET "http://localhost:8000/adagio/api/casos/?estado=PENDIENTE"

# Crear nuevo caso
curl -X POST "http://localhost:8000/adagio/api/casos/" \
  -H "Content-Type: application/json" \
  -d '{
    "cod_caso_bizagi": "CASO123",
    "num_prestamo": "98765",
    "estado": "PENDIENTE"
  }'

# Actualizar estado de caso
curl -X PATCH "http://localhost:8000/adagio/api/casos/1/" \
  -H "Content-Type: application/json" \
  -d '{"estado": "FINALIZADO"}'
```

**Respuesta de ejemplo**:
```json
{
  "id": 1,
  "cod_caso_bizagi": "CASO001",
  "num_prestamo": "12345",
  "docsoldv": "DOC123",
  "doctitulardv": "1234567890",
  "tipo_de_cuenta": "AHORROS",
  "numcta_debito": "9876543210",
  "estado": "PENDIENTE",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:30:00Z"
}
```

## 🔐 Panel de Administración

**Acceso**: `http://localhost:8000/admin/`

**Credenciales**: Use el superusuario creado durante la instalación

**Funcionalidades**:
- Gestión completa de usuarios
- CRUD avanzado de todos los modelos
- Filtros y búsquedas personalizadas
- Importación/exportación de datos

## 🚨 Solución de Problemas

### Problemas Comunes

#### Error: "No module named 'django'"
```bash
# Asegúrese de que el entorno virtual esté activado
source venv/bin/activate  # Linux/macOS
# o
venv\Scripts\activate     # Windows

# Reinstale dependencias
pip install -r requirements.txt
```

#### Error: "No such table: django_session"
```bash
# Ejecute las migraciones
python manage.py migrate
```

#### Tareas programadas no se ejecutan
```bash
# Verifique que Django-Q esté corriendo
python manage.py qcluster

# En otra terminal, verifique el estado
python manage.py qmonitor
```

#### Error al ejecutar scripts
1. **Verifique la ruta del script** sea absoluta y correcta
2. **Confirme permisos** de ejecución del archivo
3. **Valide el entorno virtual** si está especificado
4. **Revise los logs** en el detalle del proceso

### Logs del Sistema

**Logs de Django**:
- Configurados en `settings.py`
- Nivel de debug activado en desarrollo

**Logs de Procesos**:
- Almacenados en modelo `ProcessLog`
- Accesibles desde la interfaz web
- Incluyen stdout y stderr de scripts

### Base de Datos

**Backup de SQLite**:
```bash
cp db.sqlite3 db_backup_$(date +%Y%m%d).sqlite3
```

**Reset completo**:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## 📈 Mejores Prácticas

### Desarrollo de Scripts

1. **Estructura recomendada**:
   ```python
   #!/usr/bin/env python3
   import sys
   import logging
   
   def main():
       try:
           # Lógica del script
           print("Proceso iniciado...")
           # ...
           print("Proceso completado exitosamente")
           return 0
       except Exception as e:
           print(f"Error: {e}")
           return 1
   
   if __name__ == "__main__":
       sys.exit(main())
   ```

2. **Manejo de errores**: Implemente try-catch apropiados
3. **Logging**: Use print() para output visible en la interfaz
4. **Códigos de salida**: Retorne 0 para éxito, 1 para error

### Seguridad

1. **Nunca** hardcodee credenciales en scripts
2. **Use variables de entorno** para configuración sensible
3. **Valide inputs** en scripts que procesen archivos
4. **Limite permisos** de archivos y directorios

### Rendimiento

1. **Limite procesos concurrentes** (configurado en 4 por defecto)
2. **Use paginación** para grandes volúmenes de datos
3. **Optimice consultas** a la base de datos
4. **Monitoree recursos** del sistema durante ejecuciones

## 🤝 Contribuciones

### Estructura del Proyecto

```
kcique_project/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── kcique_project/          # Configuración principal
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── automations/             # App de automatizaciones
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── process_executor.py
├── adagio/                  # App de casos de débito
│   ├── models.py
│   ├── views.py
│   └── forms.py
├── templates/               # Templates HTML
├── static/                  # Archivos estáticos
└── scripts/                 # Scripts utilitarios
```

### Desarrollo

1. **Fork** el repositorio
2. **Cree una rama** para su feature: `git checkout -b feature/nueva-funcionalidad`
3. **Haga commit** de sus cambios: `git commit -am 'Agregar nueva funcionalidad'`
4. **Push** a la rama: `git push origin feature/nueva-funcionalidad`
5. **Abra un Pull Request**

## 📞 Soporte

Para soporte técnico o consultas:

- **Documentación**: Este README
- **Issues**: Reporte bugs en el repositorio
- **Logs**: Revise logs del sistema para diagnóstico

---

**© 2024 Kcique. Sistema de Gestión de Automatizaciones y Casos de Débito.** 