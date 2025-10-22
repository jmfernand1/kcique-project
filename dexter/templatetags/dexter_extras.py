from django import template
from datetime import timedelta
import json

register = template.Library()


@register.filter
def format_duration(duration):
    """
    Convierte un objeto timedelta en un string legible por humanos.
    Ej: '2 days, 3:45:12' -> '2d 3h 45m 12s'
    """
    if not isinstance(duration, timedelta):
        return duration  # Devuelve el valor original si no es un timedelta

    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 0:
        return "N/A"

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")
        
    return " ".join(parts)


@register.filter
def pprint(value):
    """
    Formatea un objeto JSON o diccionario de manera legible.
    """
    if value is None:
        return "None"
    
    try:
        if isinstance(value, str):
            # Intenta parsear si es un string JSON
            value = json.loads(value)
        return json.dumps(value, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        return str(value)

