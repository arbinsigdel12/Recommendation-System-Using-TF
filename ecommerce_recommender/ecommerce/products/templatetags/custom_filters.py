from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the arg."""
    return value * arg