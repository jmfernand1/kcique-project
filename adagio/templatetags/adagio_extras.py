from django import template
from datetime import timedelta

register = template.Library()

@register.filter(name='attr')
def attr(value, arg):
    """Adds an attribute to a form field."""
    attrs = value.field.widget.attrs
    orig_class = attrs.get('class', '')
    
    # arg is expected to be a string like "name:value;name2:value2"
    attributes_to_add = {}
    for pair in arg.split(';'):
        if ':' in pair:
            name, val = pair.split(':', 1)
            attributes_to_add[name] = val

    # Especialmente para 'class', concatenamos en lugar de reemplazar
    if 'class' in attributes_to_add and orig_class:
        attributes_to_add['class'] = f"{orig_class} {attributes_to_add['class']}"
    
    attrs.update(attributes_to_add)
    return value.as_widget(attrs=attrs)

@register.filter(name='add_class')
def add_class(value, arg):
    """Añade una clase CSS a un campo de formulario."""
    return value.as_widget(attrs={'class': arg})

@register.filter
def format_duration(duration):
    """
    Convierte un objeto timedelta en un string legible por humanos.
    Ej: '2 days, 3:45:12' -> '2d 3h 45m 12s'
    """
    if not isinstance(duration, timedelta):
        return duration # Devuelve el valor original si no es un timedelta

    total_seconds = int(duration.total_seconds())
    
    if total_seconds < 0:
        return "N/A" # O manejar duraciones negativas como prefieras

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