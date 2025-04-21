from django import template
from datetime import datetime, timedelta
from urllib.parse import urlencode

register = template.Library()

@register.filter
def format_posted_time(value):
    if not value:
        return ""
    
    now = datetime.now(value.tzinfo)
    diff = now - value
    
    months = diff.days // 30
    if months > 0:
        if months == 1:
            return "1 month ago"
        return f"{months} months ago"
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        return f"{diff.days} days ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        if minutes == 1:
            return "1 minute ago"
        return f"{minutes} minutes ago"
    
    return "Just now" 