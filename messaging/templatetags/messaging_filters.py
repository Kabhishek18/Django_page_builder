# messaging/templatetags/messaging_filters.py
from django import template
import re

register = template.Library()

@register.filter
def get_item(lst, index):
    """Get item from a list at the specified index"""
    try:
        return lst[index]
    except (IndexError, TypeError):
        return None

@register.filter
def split(value, delimiter):
    """Split a string by the specified delimiter"""
    return value.split(delimiter)

@register.filter
def format_attachment_name(path):
    """Format an attachment filename to just the filename without the path"""
    # Extract just the filename from the path
    filename = path.split('/')[-1]
    
    # If the filename is too long, truncate it
    if len(filename) > 20:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        name = name[:15] + '...'
        filename = f"{name}.{ext}" if ext else name
    
    return filename

@register.filter
def attachment_icon_class(attachment_type):
    """Return the appropriate Font Awesome icon class for the attachment type"""
    if attachment_type == 'image':
        return 'fa-image'
    elif attachment_type == 'document':
        return 'fa-file-alt'
    elif attachment_type == 'video':
        return 'fa-video'
    elif attachment_type == 'audio':
        return 'fa-volume-up'
    else:
        return 'fa-paperclip'

@register.filter
def addstr(arg1, arg2):
    """Concatenate arg1 and arg2"""
    return str(arg1) + str(arg2)

@register.filter
def is_today(date):
    """Check if the given date is today"""
    from datetime import date as date_type
    today = date_type.today()
    return date.date() == today

@register.filter
def is_yesterday(date):
    """Check if the given date is yesterday"""
    from datetime import date as date_type, timedelta
    yesterday = date_type.today() - timedelta(days=1)
    return date.date() == yesterday

@register.filter
def linebreaksbr_with_urls(text):
    """
    Convert URLs into clickable links and convert linebreaks to HTML line breaks
    """
    # URL pattern
    url_pattern = r'(https?://[^\s]+)'
    
    # Replace URLs with HTML links
    text = re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', text)
    
    # Convert linebreaks to <br>
    text = text.replace('\n', '<br>')
    
    return mark_safe(text)

from django.utils.safestring import mark_safe

@register.filter
def highlight_mentions(text, user_id=None):
    """
    Convert @username mentions to highlighted spans
    If user_id is provided, mentions of the current user will have a special class
    """
    # Mention pattern (@ followed by letters, numbers, underscores)
    mention_pattern = r'@([a-zA-Z0-9_]+)'
    
    # Replace mentions with highlighted spans
    def replacement(match):
        username = match.group(1)
        
        # If this is a mention of the current user, add special class
        if user_id and username == user_id:
            return f'<span class="mention mention-self">@{username}</span>'
        else:
            return f'<span class="mention">@{username}</span>'
    
    text = re.sub(mention_pattern, replacement, text)
    
    return mark_safe(text)