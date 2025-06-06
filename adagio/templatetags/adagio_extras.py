from django import template

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