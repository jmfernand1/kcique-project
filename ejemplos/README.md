# ejemplos/

Scripts **de ejemplo y de prueba** para consumir las APIs del proyecto. No forman
parte de la aplicación Django: son utilidades independientes para desarrolladores.

| Archivo                       | Descripción                                              |
|--------------------------------|----------------------------------------------------------|
| `ejemplo_api.py`               | Ejemplo general de consumo de la API.                    |
| `ejemplo_desembolso.py`        | Ejemplo de creación de desembolsos.                      |
| `ejemplo_cargo_simple.py`      | Ejemplo simple de cargo fijo.                            |
| `ejemplo_cargos_fijos.py`      | Ejemplo de carga de cargos fijos.                        |
| `ejemplo_dataframe_client.py`  | Ejemplo de uso del cliente basado en DataFrame.          |
| `ejemplo_uso_tracking.py`      | Ejemplo de uso del tracking ETL (usa `etl_tracking_client`). |
| `etl_tracking_client.py`       | Cliente auxiliar para el tracking ETL.                   |
| `prueba.py`, `prueba2.py`, `test.py` | Scripts de prueba / scratch.                       |
| `verificar_dexter.py`          | Script de verificación de la app dexter.                 |

Ejecutar desde la raíz del proyecto, por ejemplo:

```bash
python ejemplos/ejemplo_desembolso.py
```
