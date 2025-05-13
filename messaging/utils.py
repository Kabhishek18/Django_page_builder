# messaging/utils.py
import os
import mimetypes
from django.utils import timezone
from django.db.models import Max, F, Q, Count, Subquery, OuterRef
from django.contrib.auth.models import User

def get_user_conversations(user):
    """
    Get all conversations for a user with additional data like unread counts
    """
    from .models import Conversation, Message, Participant
    
    # Get all conversations where the user is a participant
    conversations = Conversation.objects.filter(
        participants__user=user,
        participants__is_active=True
    ).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')
    
    # Add unread count and last message to each conversation
    for conversation in conversations:
        # Get the unread count
        conversation.unread_count = conversation.get_unread_count(user)
        
        # Get the last message
        conversation.last_message = conversation.get_last_message()
        
        # Get other participants
        conversation.other_participants = conversation.participants.exclude(user=user)
    
    return conversations

def determine_file_type(file):
    """
    Determine the appropriate type for an uploaded file
    Returns one of: 'image', 'document', 'video', 'audio', 'file'
    """
    # If the file is None, return None
    if not file:
        return None
        
    # Get the file's MIME type
    mime_type, _ = mimetypes.guess_type(file.name)
    
    # If we couldn't determine the MIME type, use the extension
    if mime_type is None:
        extension = os.path.splitext(file.name.lower())[1]
        
        # Common image extensions
        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            return 'image'
        # Common document extensions
        elif extension in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt']:
            return 'document'
        # Common video extensions
        elif extension in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
            return 'video'
        # Common audio extensions
        elif extension in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            return 'audio'
        # Default
        else:
            return 'file'
    
    # Determine type based on MIME type
    if mime_type.startswith('image/'):
        return 'image'
    elif mime_type.startswith('video/'):
        return 'video'
    elif mime_type.startswith('audio/'):
        return 'audio'
    elif mime_type in ['application/pdf', 'application/msword', 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                     'application/vnd.ms-excel',
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     'application/vnd.ms-powerpoint',
                     'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                     'text/plain']:
        return 'document'
    else:
        return 'file'

def get_conversation_messages_page(conversation, page, page_size=25):
    """
    Get a page of messages for a conversation, ordered by newest to oldest
    """
    from .models import Message
    from django.core.paginator import Paginator
    
    # Get messages ordered by timestamp (descending)
    messages = conversation.messages.all().order_by('-timestamp')
    
    # Create a paginator
    paginator = Paginator(messages, page_size)
    
    # Get the requested page
    page_obj = paginator.get_page(page)
    
    # Reverse the order so messages display oldest to newest
    page_obj.object_list = list(reversed(page_obj.object_list))
    
    return page_obj

def get_users_for_conversation(exclude_user=None):
    """
    Get a list of users that can be added to a conversation
    Optionally exclude a user (typically the current user)
    """
    query = User.objects.filter(is_active=True)
    
    if exclude_user:
        query = query.exclude(id=exclude_user.id)
    
    return query.order_by('username')

def notify_new_message(message):
    """
    Handle notifications for a new message
    This is a placeholder that could be expanded to send push notifications, emails, etc.
    """
    # Mark the conversation as having unread messages for all participants except the sender
    from .models import Participant
    
    Participant.objects.filter(
        conversation=message.conversation
    ).exclude(
        user=message.sender
    ).update(
        has_unread=True
    )
    
    # Update the conversation's last_message_at timestamp
    message.conversation.last_message_at = message.timestamp
    message.conversation.save()
    
    # Here you could add code to send push notifications, emails, etc.
    # For now, we'll just return True to indicate success
    return True