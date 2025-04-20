# jitsi/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
import os
import uuid
import json

# Create a local file storage for Jitsi media
jitsi_storage = FileSystemStorage(
    location=os.path.join(settings.MEDIA_ROOT, 'jitsi'),
    base_url=settings.MEDIA_URL + 'jitsi/'
)


class JitsiRoom(models.Model):
    """
    Model for storing Jitsi meeting room information
    """
    ROOM_STATUS = (
        ('scheduled', 'Scheduled'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_rooms')
    status = models.CharField(max_length=20, choices=ROOM_STATUS, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    
    # Meeting configuration
    password_protected = models.BooleanField(default=False)
    moderator_password = models.CharField(max_length=50, blank=True, null=True)
    attendee_password = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-scheduled_at']


class JitsiParticipant(models.Model):
    """
    Model for tracking participation in Jitsi rooms
    """
    ROLE_CHOICES = (
        ('moderator', 'Moderator'),
        ('attendee', 'Attendee'),
        ('guest', 'Guest'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(JitsiRoom, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='attendee')
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} in {self.room.name}"

class JitsiCustomization(models.Model):
    """
    Model for storing Jitsi interface customization settings
    """
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    
    # Branding - use local file storage instead of S3
    logo = models.ImageField(
        upload_to='logos/', 
        storage=jitsi_storage,
        blank=True, 
        null=True
    )
    
    favicon = models.ImageField(
        upload_to='favicons/', 
        storage=jitsi_storage,
        blank=True, 
        null=True
    )
    
    background_image = models.ImageField(
        upload_to='backgrounds/', 
        storage=jitsi_storage,
        blank=True, 
        null=True
    )
    
    watermark_image = models.ImageField(
        upload_to='watermarks/', 
        storage=jitsi_storage,
        blank=True, 
        null=True
    )
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#0056E0')
    secondary_color = models.CharField(max_length=7, default='#17A0DB')
    background_color = models.CharField(max_length=7, default='#040404')
    
    # Footer
    show_footer = models.BooleanField(default=True)
    footer_text = models.CharField(max_length=255, blank=True, null=True)
    
    # Custom CSS/JS
    custom_css = models.TextField(blank=True, null=True)
    custom_js = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def clean(self):
        # Ensure only one default configuration exists
        if self.is_default and not self.pk:
            if JitsiCustomization.objects.filter(is_default=True).exists():
                raise ValidationError('There can only be one default customization.')
    
    def save(self, *args, **kwargs):
        # If this is set as default, unset all others
        if self.is_default:
            JitsiCustomization.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class JitsiFeatureConfig(models.Model):
    """
    Model for enabling/disabling Jitsi features
    """
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)
    
    # Core features
    enable_audio = models.BooleanField(default=True)
    enable_video = models.BooleanField(default=True)
    enable_chat = models.BooleanField(default=True)
    enable_screen_sharing = models.BooleanField(default=True)
    enable_recording = models.BooleanField(default=False)
    enable_livestreaming = models.BooleanField(default=False)
    enable_breakout_rooms = models.BooleanField(default=False)
    
    # Security features
    enable_lobby = models.BooleanField(default=False)
    enable_end_to_end_encryption = models.BooleanField(default=False)
    enable_password_protection = models.BooleanField(default=False)
    
    # UI features
    enable_reactions = models.BooleanField(default=True)
    enable_raise_hand = models.BooleanField(default=True)
    enable_tile_view = models.BooleanField(default=True)
    enable_filmstrip = models.BooleanField(default=True)
    
    # Additional features
    enable_polls = models.BooleanField(default=False)
    enable_whiteboard = models.BooleanField(default=False)
    enable_blur_background = models.BooleanField(default=True)
    
    # Custom configuration (stored as JSON)
    additional_config = models.JSONField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_config_dict(self):
        """Return the configuration as a dictionary for Jitsi"""
        config = {
            'startWithAudioMuted': not self.enable_audio,
            'startWithVideoMuted': not self.enable_video,
            'disableChat': not self.enable_chat,
            'desktopSharingEnabled': self.enable_screen_sharing,
            'fileRecordingsEnabled': self.enable_recording,
            'liveStreamingEnabled': self.enable_livestreaming,
            'breakoutRooms': self.enable_breakout_rooms,
            'enableLobby': self.enable_lobby,
            'e2eeEnabled': self.enable_end_to_end_encryption,
            'requirePassword': self.enable_password_protection,
            'reactionsEnabled': self.enable_reactions,
            'raiseHandEnabled': self.enable_raise_hand,
            'tileViewEnabled': self.enable_tile_view,
            'filmstripEnabled': self.enable_filmstrip,
            'pollsEnabled': self.enable_polls,
            'whiteboardEnabled': self.enable_whiteboard,
            'virtualBackgroundEnabled': self.enable_blur_background,
        }
        
        # Merge with additional_config if it exists
        if self.additional_config:
            config.update(self.additional_config)
            
        return config

class JitsiMeeting(models.Model):
    """
    Model for specific meeting instances with customization and feature configs
    """
    room = models.ForeignKey(JitsiRoom, on_delete=models.CASCADE, related_name='meetings')
    customization = models.ForeignKey(JitsiCustomization, on_delete=models.SET_NULL, null=True, blank=True)
    feature_config = models.ForeignKey(JitsiFeatureConfig, on_delete=models.SET_NULL, null=True, blank=True)
    
    meeting_id = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.subject} ({self.meeting_id})"