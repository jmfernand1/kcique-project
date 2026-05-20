"""
Hooks de preprocesamiento para drf-spectacular.

`filtrar_endpoints_dexter` deja en el esquema OpenAPI únicamente los endpoints
de la API de la app Dexter (`/dexter/api/...`), de modo que el archivo .yaml
descargable corresponda exactamente a la documentación de esta integración.
"""


def filtrar_endpoints_dexter(endpoints):
    """Mantiene solo las rutas que pertenecen a la API de Dexter."""
    return [
        (path, path_regex, method, callback)
        for (path, path_regex, method, callback) in endpoints
        if path.startswith('/dexter/api/')
    ]
