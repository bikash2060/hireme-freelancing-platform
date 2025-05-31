from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.filter
def split_lines(value):
    return value.split('\n')

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def floatformat(value, arg):
    """Format a float to a specific number of decimal places"""
    try:
        return round(float(value), int(arg))
    except (ValueError, TypeError):
        return value 