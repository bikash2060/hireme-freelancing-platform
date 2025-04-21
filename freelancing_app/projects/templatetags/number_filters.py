from django import template
import re

register = template.Library()

@register.filter
def format_currency(value):
    try:
        value = float(value)
        formatted = "{:.2f}".format(value)
        
        parts = formatted.split('.')
        integer_part = parts[0]
        decimal_part = parts[1]
        
        result = ""
        
        if len(integer_part) <= 3:
            result = integer_part
        else:
            result = integer_part[-3:]
            remaining = integer_part[:-3]
            
            while remaining:
                if len(remaining) >= 2:
                    result = remaining[-2:] + "," + result
                    remaining = remaining[:-2]
                else:
                    result = remaining + "," + result
                    break
        
        return result + "." + decimal_part
    except (ValueError, TypeError):
        return value