# jitsi/views.py
import json
import uuid
import time
import jwt
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .models import JitsiRoom, JitsiParticipant, JitsiCustomization, JitsiFeatureConfig, JitsiMeeting
from .forms import JitsiRoomForm, JitsiCustomizationForm, JitsiFeatureConfigForm
from .services import (
    generate_jwt_token, 
    get_jitsi_config, 
    apply_customization, 
    get_absolute_logo_url, 
    prepare_logo_config
)

@login_required
def dashboard(request):
    """
    Dashboard view showing the user's meetings
    """
    # Get rooms created by the user
    created_rooms = JitsiRoom.objects.filter(creator=request.user)
    
    # Get rooms where the user is a participant
    participated_rooms = JitsiRoom.objects.filter(
        participants__user=request.user
    ).exclude(creator=request.user).distinct()
    
    # Get upcoming meetings
    upcoming_meetings = created_rooms.filter(
        status='scheduled',
        scheduled_at__gte=timezone.now()
    )
    
    # Get active meetings
    active_meetings = created_rooms.filter(status='active')
    
    # Get past meetings
    past_meetings = created_rooms.filter(
        status__in=['completed', 'cancelled']
    )
    
    context = {
        'created_rooms': created_rooms,
        'participated_rooms': participated_rooms,
        'upcoming_meetings': upcoming_meetings,
        'active_meetings': active_meetings,
        'past_meetings': past_meetings,
    }
    
    return render(request, 'jitsi/dashboard.html', context)


@login_required
def create_room(request):
    """
    View for creating a new Jitsi room
    """
    if request.method == 'POST':
        form = JitsiRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.creator = request.user
            room.save()
            
            # Create a meeting instance with default configs
            default_customization = JitsiCustomization.objects.filter(is_default=True).first()
            default_feature_config = JitsiFeatureConfig.objects.filter(is_default=True).first()
            
            JitsiMeeting.objects.create(
                room=room,
                customization=default_customization,
                feature_config=default_feature_config,
                meeting_id=str(uuid.uuid4()),
                subject=room.name
            )
            
            messages.success(request, f'Room "{room.name}" created successfully!')
            return redirect('jitsi:room_detail', room_id=room.id)
    else:
        form = JitsiRoomForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'jitsi/create_room.html', context)


@login_required
def room_detail(request, room_id):
    """
    View room details and configuration
    """
    room = get_object_or_404(JitsiRoom, id=room_id)
    
    # Check if user is creator or participant
    is_creator = room.creator == request.user
    is_participant = JitsiParticipant.objects.filter(
        room=room,
        user=request.user
    ).exists()
    
    if not (is_creator or is_participant or room.is_public):
        messages.error(request, "You don't have permission to view this room.")
        return redirect('jitsi:dashboard')
    
    # Get meeting configuration
    latest_meeting = room.meetings.order_by('-created_at').first()
    
    context = {
        'room': room,
        'is_creator': is_creator,
        'is_participant': is_participant,
        'meeting': latest_meeting,
    }
    
    return render(request, 'jitsi/room_detail.html', context)




@login_required
def join_meeting(request, room_id):
    """
    Join a Jitsi meeting with improved logo handling
    """
    room = get_object_or_404(JitsiRoom, id=room_id)
    meeting = room.meetings.order_by('-created_at').first()
    
    # Determine user role
    role = 'moderator' if room.creator == request.user else 'attendee'
    
    # Create or update participant record
    participant, created = JitsiParticipant.objects.get_or_create(
        room=room,
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'role': role
        }
    )
    
    if not created:
        # Update the joined_at time and clear left_at
        participant.joined_at = timezone.now()
        participant.left_at = None
        participant.save()
    
    # If the meeting is scheduled and this is the creator joining
    if room.status == 'scheduled' and room.creator == request.user:
        room.status = 'active'
        room.save()
        
        if meeting:
            meeting.started_at = timezone.now()
            meeting.save()
    
    # Generate JWT token for authenticated access
    domain = settings.JITSI_DOMAIN
    app_id = settings.JITSI_APP_ID
    app_secret = settings.JITSI_APP_SECRET
    
    # Use room ID for token authentication
    token = generate_jwt_token(
        domain=domain,
        app_id=app_id,
        app_secret=app_secret,
        room_name=str(room.id),  # Use room ID for authentication
        user_id=str(request.user.id),
        user_name=request.user.get_full_name() or request.user.username,
        email=request.user.email,
        is_moderator=(role == 'moderator')
    )
    
    # Get room configuration
    room_config = get_jitsi_config(meeting)
    
    # Ensure room_config is a dictionary
    if not isinstance(room_config, dict):
        room_config = {}
    
    # Add subject to config to display proper meeting name
    room_config.update({
        'subject': room.name,  # Set the meeting subject to room name
        'roomDisplayName': room.name,  # Set display name
        'prejoinConfig': {
            'enabled': True,
            'hideDisplayName': False
        }
    })
    
    # Get logo configuration using helper function
    logo_config = prepare_logo_config(request, meeting)
    
    # Merge logo configuration with room configuration
    room_config.update({
        'brandingDataUrl': logo_config.get('brandingDataUrl', ''),
        'watermark': logo_config.get('watermark', {}),
        'defaultLogoUrl': logo_config.get('defaultLogoUrl', ''),
        'logoImageUrl': logo_config.get('logoImageUrl', '')
    })
    
    # Create interface config with logo settings
    interface_config = logo_config.get('interfaceConfig', {})
    interface_config.update({
        'SHOW_JITSI_WATERMARK': False,
        'SHOW_WATERMARK_FOR_GUESTS': True,
        'DEFAULT_BACKGROUND': '#ffffff',
        'HIDE_INVITE_MORE_HEADER': True,
        'TOOLBAR_BUTTONS': [
            'microphone', 'camera', 'desktop', 'fullscreen',
            'fodeviceselection', 'hangup', 'profile', 'chat',
            'settings', 'raisehand', 'videoquality', 'filmstrip',
            'tileview'
        ]
    })
    
    context = {
        'room': room,
        'meeting': meeting,
        'participant': participant,
        'token': token,
        'domain': domain,
        'config': json.dumps(room_config),
        'interface_config': json.dumps(interface_config),
        'user_info': {
            'displayName': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        },
        'is_host': role == 'moderator',
        'logo_url': logo_config.get('defaultLogoUrl', '')  # Pass logo URL to template for debugging
    }
    
    return render(request, 'jitsi/join_meeting.html', context)


@login_required
def customize_meeting(request, room_id):
    """
    View for customizing a meeting's appearance and settings
    """
    room = get_object_or_404(JitsiRoom, id=room_id)
    
    # Check if user is the creator
    if room.creator != request.user:
        messages.error(request, "Only the meeting creator can customize settings.")
        return redirect('jitsi:room_detail', room_id=room.id)
    
    if request.method == 'POST':
        # Handle form submission for meeting customization
        # Add your form handling logic here
        messages.success(request, "Meeting settings updated successfully.")
        return redirect('jitsi:room_detail', room_id=room.id)
    
    context = {
        'room': room,
        'meeting': room.meetings.order_by('-created_at').first(),
    }
    return render(request, 'jitsi/customize_meeting.html', context)

@login_required
def meeting_embed(request, room_id):
    """
    Embed view for a Jitsi meeting (iframe friendly)
    """
    room = get_object_or_404(JitsiRoom, id=room_id)
    meeting = room.meetings.order_by('-created_at').first()
    
    # Determine user role
    role = 'moderator' if room.creator == request.user else 'attendee'
    
    # Generate JWT token for authenticated access
    domain = settings.JITSI_DOMAIN
    app_id = settings.JITSI_APP_ID
    app_secret = settings.JITSI_APP_SECRET
    
    token = generate_jwt_token(
        domain=domain,
        app_id=app_id,
        app_secret=app_secret,
        room_name=str(room.id),  # Keep using room.id for consistency in JWT token
        user_id=str(request.user.id),
        user_name=request.user.get_full_name() or request.user.username,
        email=request.user.email,
        is_moderator=(role == 'moderator')
    )
    
    # Get room configuration
    room_config = get_jitsi_config(meeting)
    
    # Add custom config to show room name instead of room ID
    if not isinstance(room_config, dict):
        room_config = {}
    
    # Add subject to config to display proper meeting name
    room_config.update({
        'subject': room.name,  # Set the meeting subject to room name
        'roomDisplayName': room.name,  # Set display name
        'prejoinConfig': {
            'enabled': True,
            'hideDisplayName': False
        }
    })
    
    context = {
        'room': room,
        'meeting': meeting,
        'token': token,
        'domain': domain,
        'config': json.dumps(room_config),
        'user_info': {
            'displayName': request.user.get_full_name() or request.user.username,
            'email': request.user.email,
        },
        'return_url': request.GET.get('return_url', reverse('jitsi:room_detail', kwargs={'room_id': room.id}))
    }
    
    return render(request, 'jitsi/meeting_embed.html', context)


@csrf_exempt
def meeting_webhook(request):
    """
    Webhook for Jitsi events (participant join/leave, meeting end, etc.)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        room_id = data.get('room_id')
        
        room = JitsiRoom.objects.get(id=room_id)
        
        if event_type == 'participant_joined':
            participant_id = data.get('participant_id')
            participant = JitsiParticipant.objects.get(id=participant_id)
            participant.joined_at = timezone.now()
            participant.left_at = None
            participant.save()
            
        elif event_type == 'participant_left':
            participant_id = data.get('participant_id')
            participant = JitsiParticipant.objects.get(id=participant_id)
            participant.left_at = timezone.now()
            participant.save()
            
        elif event_type == 'meeting_ended':
            room.status = 'completed'
            room.ended_at = timezone.now()
            room.save()
            
            meeting_id = data.get('meeting_id')
            meeting = JitsiMeeting.objects.get(meeting_id=meeting_id)
            meeting.ended_at = timezone.now()
            meeting.save()
            
        return JsonResponse({'status': 'success'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def join_meeting_landing(request):
    """
    Landing page for joining a meeting
    """
    if request.method == 'POST':
        room_id = request.POST.get('room_id')
        return redirect('jitsi:join_meeting', room_id=room_id)
    
    return render(request, 'jitsi/join_meeting_landing.html')


@login_required
def end_meeting(request, room_id):
    """
    End a meeting and update its status
    """
    room = get_object_or_404(JitsiRoom, id=room_id)
    
    # Only allow creator to end meeting
    if request.user != room.creator:
        messages.error(request, "Only the meeting creator can end the meeting.")
        return redirect('jitsi:room_detail', room_id=room.id)
    
    # Update room status
    room.status = 'completed'
    room.ended_at = timezone.now()
    room.save()
    
    # Update the current meeting
    meeting = room.meetings.order_by('-created_at').first()
    if meeting:
        meeting.ended_at = timezone.now()
        meeting.save()
    
    # Update all active participants
    JitsiParticipant.objects.filter(
        room=room,
        left_at__isnull=True
    ).update(left_at=timezone.now())
    
    messages.success(request, "Meeting ended successfully.")
    return redirect('jitsi:room_detail', room_id=room.id)
