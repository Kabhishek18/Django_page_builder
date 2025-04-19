from django import template
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Get an item from a dictionary using a string key.
    Used to access values from JSON fields in templates.
    
    Usage:
    {{ settings|get_item:'key_name' }}
    """
    if not dictionary:
        return None
    
    # Handle if dictionary is a string (JSON)
    if isinstance(dictionary, str):
        try:
            dictionary = json.loads(dictionary)
        except:
            return None
    
    return dictionary.get(key, None)

@register.filter
def json_decode(json_string):
    """
    Decode a JSON string to a Python object.
    
    Usage:
    {% with data=json_string|json_decode %}
        {{ data.some_key }}
    {% endwith %}
    """
    if not json_string:
        return {}
    
    try:
        return json.loads(json_string)
    except:
        return {}