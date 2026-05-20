# docs/

Documentación del proyecto y entregables para otros equipos.

| Archivo                             | Descripción                                                       |
|-------------------------------------|-------------------------------------------------------------------|
| `Diccionario_Datos_Integracion.xlsx`| Diccionario de datos + plantillas: qué información se requiere para registrar Desembolsos, Cargos Fijos, Garantías y Casos de Débito. Entregable para equipos externos. |
| `generar_diccionario_datos.py`      | Script que genera el `.xlsx` anterior. Regenerarlo cuando cambien modelos/serializers: `python docs/generar_diccionario_datos.py`. |
| `DEXTER_API_RESUMEN.md`             | Resumen de la API de dexter.                                      |
| `TRACKING_API_RESUMEN.md`           | Resumen de la API de tracking ETL.                                |
| `RESUMEN_FRONTEND_DEXTER.md`        | Resumen del frontend de dexter.                                   |

Documentación adicional vive dentro de cada app:
- `dexter/API_DOCUMENTATION.md` — documentación completa de la API de dexter.
- `dexter/schema.yaml` — esquema OpenAPI 3 (también servido en `/api/schema/`).
