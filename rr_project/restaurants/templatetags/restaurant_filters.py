from django import template
from datetime import time

register = template.Library()

@register.filter
def time_12hour(value):
    """Convert 24-hour time to 12-hour format with AM/PM"""
    if not value:
        return ""
    
    if isinstance(value, str):
        # Handle string time format (HH:MM)
        try:
            hour, minute = value.split(':')
            hour = int(hour)
            minute = int(minute)
        except (ValueError, AttributeError):
            return value
    elif isinstance(value, time):
        hour = value.hour
        minute = value.minute
    else:
        return value
    
    # Convert to 12-hour format
    if hour == 0:
        return f"12:{minute:02d} AM"
    elif hour < 12:
        return f"{hour}:{minute:02d} AM"
    elif hour == 12:
        return f"12:{minute:02d} PM"
    else:
        return f"{hour - 12}:{minute:02d} PM"

@register.filter
def format_operating_days(value):
    """Format operating days string for display"""
    if not value:
        return "Not specified"
    
    days = [d.strip() for d in value.split(',')]
    day_names = {
        'Mon': 'Monday',
        'Tue': 'Tuesday',
        'Wed': 'Wednesday',
        'Thu': 'Thursday',
        'Fri': 'Friday',
        'Sat': 'Saturday',
        'Sun': 'Sunday'
    }
    
    formatted = [day_names.get(day, day) for day in days]
    
    if len(formatted) == 7:
        return "Daily"
    elif len(formatted) == 5 and all(d in formatted for d in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']):
        return "Mon - Fri"
    else:
        return ", ".join(formatted[:3]) + ("..." if len(formatted) > 3 else "")

