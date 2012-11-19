from django import template

register = template.Library()

@register.filter
def truncate_chars(value, limit=10):
    """
    Truncates a string after a given number of chars keeping whole words.
    
    Usage:
        {{ string|truncate_chars }}
        {{ string|truncate_chars:5 }}
    """

    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Make sure it's unicode
    value = unicode(value)

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Cut the string
    return value[:limit]