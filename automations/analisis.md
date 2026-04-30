# Análisis: ejecuciones concurrentes del mismo proceso programado

Documento de diagnóstico y cambios aplicados sobre `automations/tasks.py` y
`automations/process_executor.py` para resolver el conflicto de RPA / scraping
disparados en simultáneo por la misma tarea programada.

---

## 1. Diagnóstico

### 1.1 Configuración relevante

- `kcique_project/settings.py` → `Q_CLUSTER`: `workers: 4`, `timeout: 60`,
  `recycle: 500`.
- `automations/process_executor.py` → `MAX_CONCURRENT_PROCESSES = 4` con
  `threading.Semaphore`.
- `automations/apps.py` → `ready()` invocaba
  `reset_scheduled_tasks_on_startup()` cada vez que cargaba la app.

### 1.2 Causas raíz identificadas

#### Causa #1 — El "lock" original era local al proceso Python, no global

En `process_executor.py` antiguo:

```python
running_processes = set()
running_processes_lock = threading.Lock()
process_semaphore = threading.Semaphore(MAX_CONCURRENT_PROCESSES)
```

`set` y `threading.Lock` viven en memoria del proceso Python actual.
Django Q corre con **4 workers, que son procesos separados** (no threads).
Cada worker tenía su propia copia del `set`. Resultado:

- Si la tarea programada se dispara y la toma el worker A, marca el proceso
  como running en su memoria.
- Si en paralelo (o microsegundos después) el worker B toma la misma tarea,
  su `set` está vacío → ejecuta una segunda instancia del mismo RPA / scraper.

`is_process_running()` no tenía visibilidad cruzada entre workers.

#### Causa #2 — `run_process_threaded` desacoplaba la tarea Q del trabajo real

`run_process_threaded` lanzaba un `threading.Thread` y **retornaba al instante**.
Para Django Q la tarea terminaba en milisegundos:

- El worker quedaba libre y Django Q podía entregarle la siguiente programación
  del mismo proceso enseguida.
- `timeout: 60` no protegía porque la tarea Q ya había "terminado"; el thread
  seguía corriendo en background fuera del control de Q.
- Si el script real duraba 10 minutos y la programación era "cada 1 minuto",
  Q lanzaba ~10 ejecuciones superpuestas (limitadas solo por el semáforo y el
  set in-memory, ambos rotos por la causa #1).

#### Causa #3 — Race condition entre check y mark

`is_process_running()` en `tasks.py:28` y `mark_process_as_running()` en
`process_executor.py:184` eran **dos locks distintos en el tiempo**, no un
check-and-set atómico. Aun dentro de un mismo worker, dos invocaciones
concurrentes podían pasar ambas el check antes de que cualquiera marque.

#### Causa #4 — `apps.ready()` se ejecutaba en cada proceso Django

`reset_scheduled_tasks_on_startup()` se llamaba en `ready()`, que corre
para **cada** proceso que carga la app: el servidor web, el master de qcluster
y cada worker. Eso podía:

- Crear / recrear los `Schedule` de django-q múltiples veces casi en paralelo.
- Generar `Schedule` duplicados.
- Disparar ejecuciones inmediatas porque `next_run` quedaba en el pasado.

#### Causa #5 — El semáforo permitía 4 concurrentes del MISMO proceso

`process_semaphore = threading.Semaphore(4)` limitaba a 4 ejecuciones
**totales** dentro del mismo worker, sin distinguir por `process_id`. Si el
lock in-memory fallaba (causa #1 / #3), nada impedía que los 4 slots los
ocupara el mismo proceso.

#### Causa #6 — Sin restricción a nivel de BD

No había registro persistente de "proceso X está corriendo". `ProcessLog` se
creaba pero no se consultaba para deduplicar. Tampoco había `select_for_update`,
advisory lock ni un campo `is_running` en `AutomatedProcess`.

### 1.3 Síntoma observable

Para una tarea "cada N minutos" cuyo script tardaba más de N minutos
(típico en scraping / RPA): los 4 workers de Q tomaban las invocaciones
sucesivas, cada uno creía que nadie estaba corriendo, todos lanzaban threads y
terminaba con 2 a 4 navegadores / sesiones RPA encimados peleándose por el
mismo recurso (driver de Selenium, archivo, sesión web, etc.).

---

## 2. Cambios aplicados

### 2.1 Lock a nivel de base de datos (`AutomatedProcess`)

`automations/models.py` agrega dos campos:

```python
is_running = models.BooleanField(default=False, ...)
running_started_at = models.DateTimeField(null=True, blank=True, ...)
```

Defaults seguros para producción: el `ALTER TABLE` que produce la migración
es aditivo y no toca data existente.

### 2.2 `process_executor.py` reescrito

- `acquire_run_lock(process_id)` → adquiere el lock de forma **atómica** con
  `transaction.atomic` + `select_for_update`. Esto serializa correctamente
  entre los 4 workers de Q.
- Detección de **locks rancios**: si `running_started_at` supera
  `STALE_LOCK_AFTER_MINUTES` (180 min), se libera automáticamente. Cubre el
  caso de un worker que cae sin liberar el lock.
- `release_run_lock(process_id)` → idempotente, en `finally`.
- `execute_script(process_id)` → ahora es **sincrónico**. Sin
  `threading.Thread` interno, sin `Semaphore`. El worker de Q queda ocupado
  durante toda la duración del subprocess.
- `run_process_safely(process_id)` → único punto de entrada: adquiere lock y
  ejecuta sincrónicamente.
- `run_process_threaded(process_id)` → mantenido para compatibilidad. Ahora
  despacha vía `async_task('automations.process_executor.run_process_safely', ...)`,
  para que tanto los disparos manuales como los programados pasen por la
  misma cola Q y respeten el lock.

### 2.3 `tasks.py` simplificado

`execute_automated_process(*args, **kwargs)`:

1. Resuelve `task_id`.
2. Verifica que el `AutomatedProcess` exista y esté `is_active`.
3. Pre-chequeo barato vía `is_process_running` (consulta a la BD).
4. Aplica el filtro de `hora_inicio` / `hora_fin` para frecuencias
   `MINUTOS` / `HORAS`.
5. Llama a `run_process_safely(task_id)` → ejecución sincrónica con lock
   atómico.

### 2.4 `apps.py` ya no resetea schedules en `ready()`

`AutomationsConfig.ready()` queda sin lógica. La razón está documentada en el
docstring: el reset duplicado por proceso causaba schedules paralelos.

### 2.5 Management command `reset_schedules`

Nuevo: `automations/management/commands/reset_schedules.py`.

- Libera todos los `is_running=True` rancios al arrancar (`--skip-locks`
  permite saltarlo).
- Llama a `reset_scheduled_tasks_on_startup()` (que ya existía en
  `models.py`).
- Imprime resumen.

### 2.6 `iniciar_cluster.bat`

```bat
call kcique\Scripts\Activate.bat
call python manage.py reset_schedules
call python manage.py qcluster
```

El reset corre **una sola vez** antes de levantar el cluster, no una vez por
worker.

### 2.7 `Q_CLUSTER` actualizado

```python
"timeout": 1800,   # 30 minutos por tarea (antes 60s).
"retry": 1860,     # > timeout para evitar reintentos prematuros.
"max_attempts": 1, # No reintentar tareas fallidas (evita re-disparar RPAs).
```

`timeout: 60` provocaba que Django Q considerara muerta la tarea, la
re-encolara y se ejecutara de nuevo aunque el script siguiera corriendo.

### 2.8 Admin

`AutomatedProcessAdmin` ahora:

- Muestra `is_running` y `running_started_at` en la lista y en el detalle.
- Filtra por `is_running`.
- Expone una acción **"Liberar lock de ejecución (forzar)"** para destrabar
  manualmente procesos que hayan quedado marcados como running tras un crash.

### 2.9 `views.py`

`run_process_view` chequea `is_process_running` antes de encolar y muestra un
mensaje claro al usuario si el proceso ya está corriendo, en vez de encolar
ciegamente.

---

## 3. Despliegue en producción

Pasos en orden:

1. `git pull` de la rama `bugdobejec`.
2. Detener el servicio de qcluster (y opcionalmente el web, aunque no es
   imprescindible).
3. Generar y aplicar la migración:

   ```bash
   python manage.py makemigrations automations
   python manage.py migrate
   ```

   La migración agrega solo dos columnas con defaults; no rompe data existente.
4. Levantar el cluster con `iniciar_cluster.bat` (que ahora ejecuta
   `reset_schedules` automáticamente antes de `qcluster`).
5. Levantar el web con `iniciar_kcique.bat`.

### Verificación post-deploy

- En el admin, los procesos no deberían quedar con `is_running = True`
  permanentemente. Si alguno queda marcado, usar la acción
  **"Liberar lock de ejecución"** o ejecutar `python manage.py reset_schedules`.
- Forzar la ejecución manual del mismo proceso dos veces seguidas desde la
  UI: la segunda debe avisar que ya está en ejecución.
- Programar una tarea de prueba cada 1 minuto cuyo script duerma 5 minutos:
  no deben aparecer ejecuciones superpuestas en `ProcessLog`.

---

## 4. Resumen técnico de la solución

| Problema | Antes | Ahora |
|---|---|---|
| Lock | `set()` in-memory por worker | Campo `is_running` en BD + `select_for_update` |
| Atomicidad | Check y mark separados | `transaction.atomic` |
| Visibilidad cross-worker | Ninguna | Total (BD compartida) |
| Recuperación tras crash | Manual / reinicio | `STALE_LOCK_AFTER_MINUTES` + `reset_schedules` |
| Modelo de ejecución | Thread spawneado, tarea Q termina al instante | Ejecución sincrónica dentro del worker Q |
| Reintentos de Q | `timeout=60` con retries por defecto | `timeout=1800`, `retry=1860`, `max_attempts=1` |
| Reset de schedules | En `ready()` (1 vez por proceso Django) | Management command (1 vez por arranque del cluster) |
