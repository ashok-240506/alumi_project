from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()

@register.filter
def short_timesince(value):
    """
    Returns a short timesince format:
    2 hr 38 min, 1 day, 5 hr
    """
    if not value:
        return ""
    
    # Get full timesince string
    full = timesince(value, now())
    
    # Take only first two units
    parts = full.split(", ")
    short_parts = []
    
    for part in parts[:2]:
        if "year" in part:
            short_parts.append(part.replace("years", "yr").replace("year", "yr"))
        elif "month" in part:
            short_parts.append(part.replace("months", "mo").replace("month", "mo"))
        elif "week" in part:
            short_parts.append(part.replace("weeks", "wk").replace("week", "wk"))
        elif "day" in part:
            short_parts.append(part.replace("days", "day").replace("day", "day"))
        elif "hour" in part:
            short_parts.append(part.replace("hours", "hr").replace("hour", "hr"))
        elif "minute" in part:
            short_parts.append(part.replace("minutes", "min").replace("minute", "min"))
        elif "second" in part:
            short_parts.append(part.replace("seconds", "sec").replace("second", "sec"))
    
    return " ".join(short_parts)
