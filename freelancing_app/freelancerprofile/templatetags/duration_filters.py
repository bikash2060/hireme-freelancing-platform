# In your app's templatetags folder
# duration_filters.py
from django import template
from datetime import datetime
import math

register = template.Library()

@register.filter
def months_between(start_date, end_date):
    if not end_date:  # Handle the case for "Present"
        end_date = datetime.now().date()
    
    total_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    
    # Round up if there are additional days
    if end_date.day > start_date.day:
        total_months += 1
    
    # Calculate years and remaining months
    years = total_months // 12
    remaining_months = total_months % 12
    
    # Format the output based on years and months
    if years == 0:
        return f"{total_months} month{'s' if total_months != 1 else ''}"
    elif remaining_months == 0:
        return f"{years} year{'s' if years > 1 else ''}"
    else:
        return f"{years} year{'s' if years > 1 else ''} {remaining_months} month{'s' if remaining_months != 1 else ''}"