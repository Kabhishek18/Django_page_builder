# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Q, Max, OuterRef, Subquery
from django.views.decorators.http import require_POST

from .models import Conversation, Participant, Message
from .forms import MessageForm, PrivateConversationForm, GroupConversationForm, BroadcastForm
from .serializers import (
    MessageSerializer, MessageActionSerializer, MessageListSerializer,
    ConversationSerializer, ConversationDetailSerializer
)
from .utils import get_user_conversations, get_conversation_messages_page, get_users_for_conversation


@login_required
def inbox(request):
    """Main inbox view showing all conversations for the current user"""
    user = request.user
    
    # Get all conversations for this user with unread counts
    conversations = get_user_conversations(user)
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'active_tab': 'inbox',
        'page_title': 'Messages',
    })


@login_required
def conversation_detail(request, conversation_id):
    """View a specific conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    try:
        participant = Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_active=True
        )
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this conversation.")
        return redirect('messaging:inbox')
    
    # Get messages, paginated
    messages_page = get_conversation_messages_page(conversation, request.GET.get('page', 1))
    
    # Get all participants
    participants = conversation.participants.filter(is_active=True)
    
    # Create form for new message
    form = MessageForm()
    
    # Get all user conversations for the sidebar
    all_conversations = get_user_conversations(request.user)
    
    # Mark the conversation as read
    conversation.mark_as_read(request.user)
    
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_page,
        'participants': participants,
        'form': form,
        'is_admin': participant.is_admin,
        'conversations': all_conversations,
        'active_conversation': conversation,
        'active_tab': 'inbox',
        'page_title': f'Conversation with {conversation}',
    })


@login_required
@require_POST
def send_message(request, conversation_id):
    """Send a new message in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user, 
            is_active=True
        )
    except Participant.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Not a participant'}, status=403)
        messages.error(request, "You cannot send messages in this conversation.")
        return redirect('messaging:inbox')
    
    form = MessageForm(request.POST, request.FILES)
    
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.sender = request.user
        
        # Handle attachment type detection (done in Message.save)
        message.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # For AJAX requests, return JSON
            serializer = MessageSerializer(message)
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.strftime('%b %d, %Y, %I:%M %p'),
                    'has_attachment': bool(message.attachment),
                    'attachment_url': message.get_attachment_url(),
                    'attachment_type': message.attachment_type,
                }
            })
        
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    messages.error(request, "There was an error sending your message.")
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)


@login_required
def load_messages(request, conversation_id):
    """Load more messages in a conversation (AJAX)"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_active=True
        )
    except Participant.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Not a participant'}, status=403)
    
    # Get last message ID from request
    last_id = request.GET.get('last_id')
    limit = int(request.GET.get('limit', 20))
    
    # Query messages before the last_id
    messages_query = conversation.messages.all()
    if last_id:
        messages_query = messages_query.filter(id__lt=last_id)
    
    messages_list = messages_query.order_by('-timestamp')[:limit]
    
    # Format messages for JSON response
    messages_data = []
    for message in messages_list:
        messages_data.append({
            'id': message.id,
            'content': message.content,
            'sender_id': message.sender.id if message.sender else None,
            'sender_name': str(message.sender) if message.sender else "Unknown",
            'is_self': message.sender == request.user,
            'timestamp': message.timestamp.strftime('%b %d, %Y, %I:%M %p'),
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted,
            'has_attachment': bool(message.attachment),
            'attachment_url': message.get_attachment_url(),
            'attachment_type': message.attachment_type,
        })
    
    return JsonResponse({
        'status': 'success',
        'messages': messages_data,
        'has_more': len(messages_list) == limit,
    })


@login_required
@require_POST
def mark_as_read(request, conversation_id):
    """Mark a conversation as read"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    participant = get_object_or_404(
        Participant, 
        conversation=conversation, 
        user=request.user,
        is_active=True
    )
    
    # Mark as read
    participant.mark_as_read()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)


@login_required
@require_POST
def edit_message(request, message_id):
    """Edit a message"""
    message = get_object_or_404(Message, id=message_id)
    
    # Check if user is the sender
    if message.sender != request.user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
        return HttpResponseForbidden("You cannot edit this message")
    
    # Get new content
    new_content = request.POST.get('content')
    if not new_content:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Content is required'}, status=400)
        messages.error(request, "Message content cannot be empty.")
        return redirect('messaging:conversation_detail', conversation_id=message.conversation.id)
    
    # Edit the message
    message.edit_message(new_content)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        serializer = MessageActionSerializer({
            'id': message.id,
            'content': message.content,
            'edited_at': message.edited_at,
        })
        return JsonResponse({
            'status': 'success',
            'message': serializer.data
        })
    
    return redirect('messaging:conversation_detail', conversation_id=message.conversation.id)


@login_required
@require_POST
def delete_message(request, message_id):
    """Delete (soft delete) a message"""
    message = get_object_or_404(Message, id=message_id)
    conversation_id = message.conversation.id
    
    # Check if user is the sender or an admin of the conversation
    is_sender = message.sender == request.user
    is_admin = Participant.objects.filter(
        conversation=message.conversation, 
        user=request.user,
        is_admin=True,
        is_active=True
    ).exists()
    
    if not (is_sender or is_admin):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Not authorized'}, status=403)
        return HttpResponseForbidden("You cannot delete this message")
    
    # Delete the message
    message.delete_message()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('messaging:conversation_detail', conversation_id=conversation_id)


@login_required
def new_private_conversation(request):
    """Create a new private (1-1) conversation"""
    if request.method == 'POST':
        form = PrivateConversationForm(request.POST, user=request.user)
        
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            message_content = form.cleaned_data['message']
            
            # Check if a conversation already exists between these users
            existing_conversation = None
            
            # Find private conversations where both users are participants
            user_conversations = Conversation.objects.filter(
                participants__user=request.user,
                type='private'
            )
            
            for conv in user_conversations:
                # If this is a private convo with exactly 2 participants including recipient
                if (conv.participants.count() == 2 and 
                    conv.participants.filter(user=recipient, is_active=True).exists()):
                    existing_conversation = conv
                    break
            
            # Create new conversation if none exists
            if not existing_conversation:
                conversation = Conversation.objects.create(
                    type='private',
                    creator=request.user
                )
                
                # Add participants
                conversation.add_participant(request.user)
                conversation.add_participant(recipient)
            else:
                conversation = existing_conversation
            
            # Add message
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_content
            )
            
            messages.success(request, f"Message sent to {recipient}.")
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    else:
        # Pre-fill recipient if specified in GET request
        recipient_id = request.GET.get('recipient')
        initial = {}
        
        if recipient_id:
            try:
                recipient = User.objects.get(id=recipient_id)
                initial['recipient'] = recipient
            except User.DoesNotExist:
                pass
                
        form = PrivateConversationForm(user=request.user, initial=initial)
    
    return render(request, 'messaging/new_private_conversation.html', {
        'form': form,
        'active_tab': 'new_message',
        'page_title': 'New Message',
    })


@login_required
def new_group_conversation(request):
    """Create a new group conversation"""
    if request.method == 'POST':
        form = GroupConversationForm(request.POST, request.FILES, user=request.user)
        
        if form.is_valid():
            conversation = form.save(commit=True, creator=request.user)
            messages.success(request, f"Group '{conversation.name}' created successfully.")
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    else:
        form = GroupConversationForm(user=request.user)
    
    return render(request, 'messaging/new_group_conversation.html', {
        'form': form,
        'active_tab': 'new_group',
        'page_title': 'New Group Chat',
    })


@login_required
def new_broadcast(request):
    """Create a new broadcast message"""
    if request.method == 'POST':
        form = BroadcastForm(request.POST, user=request.user)
        
        if form.is_valid():
            conversation = form.save(commit=True, sender=request.user)
            messages.success(request, "Broadcast message sent successfully.")
            return redirect('messaging:inbox')
    else:
        form = BroadcastForm(user=request.user)
    
    return render(request, 'messaging/new_broadcast.html', {
        'form': form,
        'active_tab': 'new_broadcast',
        'page_title': 'New Broadcast',
    })


@login_required
def manage_group(request, conversation_id):
    """Manage a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if user is an admin of this group
    participant = get_object_or_404(
        Participant, 
        conversation=conversation, 
        user=request.user,
        is_admin=True,
        is_active=True
    )
    
    # Get all participants
    participants = conversation.participants.filter(is_active=True)
    
    # Get users who can be added to the group
    available_users = get_users_for_conversation(exclude_user=request.user)
    
    # Filter out users who are already in the group
    existing_user_ids = participants.values_list('user_id', flat=True)
    available_users = available_users.exclude(id__in=existing_user_ids)
    
    # Handle group info updates
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            conversation.name = name
            conversation.description = description
            
            # Handle image upload
            if 'image' in request.FILES:
                conversation.image = request.FILES['image']
                
            conversation.save()
            messages.success(request, "Group information updated successfully.")
            return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    return render(request, 'messaging/manage_group.html', {
        'conversation': conversation,
        'participants': participants,
        'available_users': available_users,
        'active_tab': 'inbox',
        'page_title': f'Manage {conversation.name}',
    })


@login_required
@require_POST
def add_group_member(request, conversation_id):
    """Add a new member to a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if user is an admin of this group
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_admin=True,
            is_active=True
        )
    except Participant.DoesNotExist:
        messages.error(request, "You don't have permission to add members to this group.")
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Get user to add
    user_id = request.POST.get('user_id')
    try:
        user_to_add = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Check if user is already in the group
    if conversation.participants.filter(user=user_to_add, is_active=True).exists():
        messages.info(request, f"{user_to_add} is already a member of this group.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Add the user
    conversation.add_participant(user_to_add)
    
    # Create system message about the new member
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=f"{user_to_add} has been added to the group."
    )
    
    messages.success(request, f"{user_to_add} added to the group successfully.")
    return redirect('messaging:manage_group', conversation_id=conversation.id)


@login_required
def remove_group_member(request, conversation_id, user_id):
    """Remove a member from a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if user is an admin of this group or removing themselves
    is_admin = Participant.objects.filter(
        conversation=conversation, 
        user=request.user,
        is_admin=True,
        is_active=True
    ).exists()
    
    is_self = int(user_id) == request.user.id
    
    if not (is_admin or is_self):
        messages.error(request, "You don't have permission to remove members from this group.")
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Get user to remove
    try:
        user_to_remove = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Check if user is in the group
    if not conversation.participants.filter(user=user_to_remove, is_active=True).exists():
        messages.info(request, f"{user_to_remove} is not a member of this group.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Cannot remove the last admin
    if user_to_remove == request.user and is_admin:
        # Check if this is the last admin
        admin_count = conversation.participants.filter(is_admin=True, is_active=True).count()
        if admin_count <= 1:
            messages.error(request, "You cannot leave the group as you are the last admin. Please make someone else an admin first.")
            return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Remove the user
    conversation.remove_participant(user_to_remove)
    
    # Create system message about the member removal
    if is_self:
        message_text = f"{user_to_remove} has left the group."
    else:
        message_text = f"{user_to_remove} has been removed from the group by {request.user}."
    
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=message_text
    )
    
    if is_self:
        messages.success(request, "You have left the group.")
        return redirect('messaging:inbox')
    
    messages.success(request, f"{user_to_remove} removed from the group successfully.")
    return redirect('messaging:manage_group', conversation_id=conversation.id)


@login_required
def leave_group(request, conversation_id):
    """Leave a group conversation"""
    # This is a redirect to remove_group_member with the current user's ID
    return redirect('messaging:remove_group_member', 
                   conversation_id=conversation_id, 
                   user_id=request.user.id)


@login_required
def message_notifications(request):
    """Get unread message notifications for the user (AJAX)"""
    # Get conversations with unread messages
    user_conversations = get_user_conversations(request.user)
    
    unread_conversations = []
    total_unread = 0
    
    for conversation in user_conversations:
        if conversation.unread_count > 0:
            total_unread += conversation.unread_count
            
            # Get conversation preview data
            last_message = conversation.last_message
            sender_name = last_message.sender.username if last_message and last_message.sender else "Unknown"
            
            # Get conversation name/title
            if conversation.name:
                conversation_name = conversation.name
            elif conversation.type == 'private':
                # For private conversations, show the other user's name
                other_participant = conversation.participants.exclude(user=request.user).first()
                conversation_name = other_participant.user.username if other_participant else "Private Conversation"
            else:
                conversation_name = f"{conversation.get_type_display()} #{conversation.id}"
            
            unread_conversations.append({
                'id': conversation.id,
                'name': conversation_name,
                'unread_count': conversation.unread_count,
                'last_message_preview': last_message.content[:50] + '...' if last_message and len(last_message.content) > 50 else (last_message.content if last_message else ""),
                'sender_name': sender_name,
                'timestamp': last_message.timestamp.strftime('%b %d, %Y, %I:%M %p') if last_message else "",
            })
    
    return JsonResponse({
        'status': 'success',
        'total_unread': total_unread,
        'unread_conversations': unread_conversations,
    })


@login_required
def unread_count(request):
    """Get total unread message count for the user (AJAX)"""
    user_conversations = get_user_conversations(request.user)
    
    total_unread = sum(c.unread_count for c in user_conversations)
    
    return JsonResponse({
        'status': 'success',
        'total_unread': total_unread,
    })


@login_required
@require_POST
def make_group_admin(request, conversation_id, user_id):
    """Make a user an admin of a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if current user is an admin
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_admin=True,
            is_active=True
        )
    except Participant.DoesNotExist:
        messages.error(request, "You don't have permission to manage group admins.")
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Get participant to make admin
    participant = get_object_or_404(
        Participant, 
        conversation=conversation, 
        user_id=user_id,
        is_active=True
    )
    
    # Make the participant an admin
    participant.is_admin = True
    participant.save()
    
    # Create system message
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=f"{participant.user} is now a group admin."
    )
    
    messages.success(request, f"{participant.user} is now a group admin.")
    return redirect('messaging:manage_group', conversation_id=conversation.id)


@login_required
@require_POST
def remove_group_admin(request, conversation_id, user_id):
    """Remove admin status from a user in a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if current user is an admin
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_admin=True,
            is_active=True
        )
    except Participant.DoesNotExist:
        messages.error(request, "You don't have permission to manage group admins.")
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Get participant to remove admin status
    participant = get_object_or_404(
        Participant, 
        conversation=conversation, 
        user_id=user_id,
        is_admin=True,
        is_active=True
    )
    
    # Cannot remove the last admin
    admin_count = conversation.participants.filter(is_admin=True, is_active=True).count()
    if admin_count <= 1:
        messages.error(request, "Cannot remove the last admin from the group.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Remove admin status
    participant.is_admin = False
    participant.save()
    
    # Create system message
    Message.objects.create(
        conversation=conversation,
        sender=request.user,
        content=f"{participant.user} is no longer a group admin."
    )
    
    messages.success(request, f"{participant.user} is no longer a group admin.")
    return redirect('messaging:manage_group', conversation_id=conversation.id)


@login_required
@require_POST
def delete_group(request, conversation_id):
    """Delete a group conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id, type='group')
    
    # Check if user is an admin of this group
    try:
        Participant.objects.get(
            conversation=conversation, 
            user=request.user,
            is_admin=True,
            is_active=True
        )
    except Participant.DoesNotExist:
        messages.error(request, "You don't have permission to delete this group.")
        return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    # Instead of actually deleting the conversation, mark it as inactive
    conversation.is_active = False
    conversation.save()
    
    # Mark all participants as inactive
    conversation.participants.update(is_active=False)
    
    messages.success(request, f"Group '{conversation.name}' has been deleted.")
    return redirect('messaging:inbox')