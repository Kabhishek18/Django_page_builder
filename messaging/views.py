# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q, Max, OuterRef, Subquery
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from .models import Conversation, Participant, Message
from .forms import MessageForm, PrivateConversationForm, GroupConversationForm, BroadcastForm


@login_required
def inbox(request):
    """Main inbox view showing all conversations for the current user"""
    user = request.user
    
    # Get all conversations where the user is a participant
    conversations = Conversation.objects.filter(
        participants__user=user,
        participants__is_active=True
    ).annotate(
        last_message_time=Max('messages__timestamp')
    ).order_by('-last_message_time')

    # Get unread counts for each conversation
    for conversation in conversations:
        conversation.unread_count = conversation.get_unread_count(user)
        
        # Get the last message for preview
        last_message = conversation.get_last_message()
        conversation.last_message = last_message
        
        # Get other participants for display
        other_participants = conversation.participants.exclude(user=user)
        conversation.other_participants = other_participants
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations,
        'user': user,
    })


@login_required
def conversation_detail(request, conversation_id):
    """View a specific conversation and its messages"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    try:
        participant = Participant.objects.get(conversation=conversation, user=request.user)
    except Participant.DoesNotExist:
        messages.error(request, "You are not a participant in this conversation.")
        return redirect('messaging:inbox')
    
    # Mark the conversation as read
    conversation.mark_as_read(request.user)
    
    # Get messages, paginated
    message_list = conversation.get_messages()
    paginator = Paginator(message_list, 50)  # 50 messages per page
    
    page = request.GET.get('page')
    messages_page = paginator.get_page(page)
    
    # Get participants
    participants = conversation.participants.all()
    
    # Create form for new message
    form = MessageForm()
    
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_page,
        'participants': participants,
        'form': form,
        'is_admin': participant.is_admin,
    })


@login_required
@require_POST
def send_message(request, conversation_id):
    """Send a new message in a conversation"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check if user is a participant
    try:
        Participant.objects.get(conversation=conversation, user=request.user, is_active=True)
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
        
        # Handle attachment type detection
        if message.attachment:
            filename = message.attachment.name.lower()
            if filename.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                message.attachment_type = 'image'
            elif filename.endswith(('.mp4', '.avi', '.mov')):
                message.attachment_type = 'video'
            elif filename.endswith(('.mp3', '.wav', '.ogg')):
                message.attachment_type = 'audio'
            elif filename.endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx')):
                message.attachment_type = 'document'
            else:
                message.attachment_type = 'file'
        
        message.save()
        
        # Update conversation's last_message_at
        conversation.last_message_at = timezone.now()
        conversation.save()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'timestamp': message.timestamp.strftime('%b %d, %Y, %I:%M %p'),
                    'has_attachment': bool(message.attachment),
                    'attachment_url': message.attachment.url if message.attachment else None,
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
        Participant.objects.get(conversation=conversation, user=request.user)
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
            'attachment_url': message.attachment.url if message.attachment else None,
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
    participant = get_object_or_404(Participant, conversation=conversation, user=request.user)
    
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
        return JsonResponse({
            'status': 'success',
            'message': {
                'id': message.id,
                'content': message.content,
                'edited_at': message.edited_at.strftime('%b %d, %Y, %I:%M %p'),
            }
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
        is_admin=True
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
            
            # Find conversations where both users are participants
            user_conversations = Conversation.objects.filter(
                participants__user=request.user,
                type='private'
            )
            
            for conv in user_conversations:
                # If this is a private convo with exactly 2 participants including recipient
                if (conv.participants.count() == 2 and 
                    conv.participants.filter(user=recipient).exists()):
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
            
            # Update conversation timestamp
            conversation.last_message_at = timezone.now()
            conversation.save()
            
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
        is_admin=True
    )
    
    # Get all participants
    participants = conversation.participants.all()
    
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
            is_admin=True
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
    if conversation.participants.filter(user=user_to_add).exists():
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
        is_admin=True
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
    if not conversation.participants.filter(user=user_to_remove).exists():
        messages.info(request, f"{user_to_remove} is not a member of this group.")
        return redirect('messaging:manage_group', conversation_id=conversation.id)
    
    # Cannot remove the last admin
    if user_to_remove == request.user and is_admin:
        # Check if this is the last admin
        admin_count = conversation.participants.filter(is_admin=True).count()
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
    user_conversations = Conversation.objects.filter(participants__user=request.user)
    
    unread_conversations = []
    total_unread = 0
    
    for conversation in user_conversations:
        unread_count = conversation.get_unread_count(request.user)
        if unread_count > 0:
            total_unread += unread_count
            
            # Get conversation preview data
            last_message = conversation.get_last_message()
            sender_name = last_message.sender.username if last_message and last_message.sender else "Unknown"
            
            # Get conversation name/title
            if conversation.name:
                conversation_name = conversation.name
            elif conversation.type == 'private':
                # For private conversations, show the other user's name
                other_user = conversation.participants.exclude(user=request.user).first()
                conversation_name = other_user.user.username if other_user else "Private Conversation"
            else:
                conversation_name = f"{conversation.get_type_display()} #{conversation.id}"
            
            unread_conversations.append({
                'id': conversation.id,
                'name': conversation_name,
                'unread_count': unread_count,
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
    # Get conversations with unread messages
    user_conversations = Conversation.objects.filter(participants__user=request.user)
    
    total_unread = 0
    for conversation in user_conversations:
        total_unread += conversation.get_unread_count(request.user)
    
    return JsonResponse({
        'status': 'success',
        'total_unread': total_unread,
    })