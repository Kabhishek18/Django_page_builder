# messaging/templatetags/messaging_filters.py
from django import template
import re
from datetime import date, datetime, timedelta
from django.utils import timezone

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
    today = date.today()
    return date.date() == today

@register.filter
def is_yesterday(date):
    """Check if the given date is yesterday"""
    yesterday = date.today() - timedelta(days=1)
    return date.date() == yesterday

@register.filter
def time_ago(timestamp):
    """
    Return a human-readable time difference from now
    e.g., "2 hours ago" or "Just now"
    """
    if not timestamp:
        return ''
        
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return timestamp
    
    now = timezone.now()
    
    if timezone.is_naive(timestamp):
        timestamp = timezone.make_aware(timestamp)
    
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    
    minutes = int(seconds / 60)
    if minutes < 60:
        return f"{minutes}m ago"
    
    hours = int(minutes / 60)
    if hours < 24:
        return f"{hours}h ago"
    
    days = int(hours / 24)
    if days < 7:
        return f"{days}d ago"
    
    if days < 31:
        weeks = int(days / 7)
        return f"{weeks}w ago"
    
    months = int(days / 30.44)
    if months < 12:
        return f"{months}mo ago"
    
    years = int(days / 365.25)
    return f"{years}y ago"

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
        if user_id and str(username) == str(user_id):
            return f'<span class="mention mention-self">@{username}</span>'
        else:
            return f'<span class="mention">@{username}</span>'
    
    text = re.sub(mention_pattern, replacement, text)
    
    return mark_safe(text)

@register.filter
def make_initials(username):
    """
    Get initials from username for avatars
    """
    if not username:
        return "?"
        
    # If it contains a space, use first letter of first and last name
    if ' ' in username:
        names = username.split()
        return (names[0][0] + names[-1][0]).upper()
    
    # If it's a single word, use first two letters or just first if too short
    if len(username) >= 2:
        return username[:2].upper()
    else:
        return username.upper()

@register.filter
def message_day_format(timestamp):
    """
    Format the date for messages based on how recent it is
    """
    if not timestamp:
        return ""
        
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                timestamp = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            except ValueError:
                return timestamp
    
    now = timezone.now()
    timestamp_date = timestamp.date()
    
    if timestamp_date == now.date():
        return "Today"
    elif timestamp_date == (now - timedelta(days=1)).date():
        return "Yesterday"
    elif (now - timestamp).days < 7:
        return timestamp.strftime('%A')  # Weekday name
    else:
        return timestamp.strftime('%b %d, %Y')  # e.g. Jan 15, 2023

@register.filter
def emoji_replace(text):
    """
    Replace text emoji like :) with unicode emoji
    """
    emoji_map = {
        ':)': '😊',
        ':(': '😞',
        ':D': '😃',
        ';)': '😉',
        ':P': '😋',
        ':p': '😋',
        '<3': '❤️',
        ':heart:': '❤️',
        ':thumbsup:': '👍',
        ':thumbs_up:': '👍',
        ':thumbsdown:': '👎',
        ':thumbs_down:': '👎',
        ':+1:': '👍',
        ':-1:': '👎',
        ':wave:': '👋',
        ':fire:': '🔥',
        ':smile:': '😄',
        ':laugh:': '😂',
        ':laughing:': '😂',
        ':sob:': '😭',
        ':thinking:': '🤔',
        ':clap:': '👏',
        ':pray:': '🙏',
        ':tada:': '🎉',
        ':party:': '🎊',
    }
    
    for key, value in emoji_map.items():
        text = text.replace(key, value)
    
    return text