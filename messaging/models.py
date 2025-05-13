# messaging/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.urls import reverse

class Conversation(models.Model):
    """
    Conversation model to track different chat types:
    - 1-1 private conversations
    - Group chats 
    - Broadcast messages
    """
    CONVERSATION_TYPES = (
        ('private', _('Private (1-1)')),
        ('group', _('Group Chat')),
        ('broadcast', _('Broadcast')),
    )
    
    name = models.CharField(_('Name'), max_length=100, blank=True, null=True)
    type = models.CharField(_('Type'), max_length=20, choices=CONVERSATION_TYPES, default='private')
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_conversations')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    last_message_at = models.DateTimeField(_('Last Message At'), default=timezone.now)
    
    # For group and broadcast conversations
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='conversations/', blank=True, null=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-last_message_at']
    
    def __str__(self):
        if self.name:
            return self.name
        elif self.type == 'private':
            participants = self.participants.all()
            if participants.count() == 2:
                return f"Chat between {participants[0].user} and {participants[1].user}"
            else:
                return f"Private chat created on {self.created_at.strftime('%Y-%m-%d')}"
        else:
            return f"{self.get_type_display()} created on {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_absolute_url(self):
        """Return the URL for this conversation"""
        return reverse('messaging:conversation_detail', kwargs={'conversation_id': self.id})
    
    def get_participants_display(self):
        """Return a comma-separated list of participant names"""
        return ", ".join([str(p.user) for p in self.participants.all()])
    
    def add_participant(self, user, is_admin=False):
        """Add a user to this conversation"""
        participant, created = Participant.objects.get_or_create(
            conversation=self,
            user=user,
            defaults={'is_admin': is_admin, 'is_active': True}
        )
        
        # If the participant existed but was inactive, reactivate them
        if not created and not participant.is_active:
            participant.is_active = True
            participant.save()
            
        return participant
    
    def remove_participant(self, user):
        """Remove a user from this conversation"""
        Participant.objects.filter(conversation=self, user=user).update(is_active=False)
    
    def get_messages(self):
        """Get all messages for this conversation, ordered by timestamp"""
        return self.messages.all().order_by('timestamp')
    
    def get_last_message(self):
        """Get the most recent message in this conversation"""
        return self.messages.order_by('-timestamp').first()
    
    def get_unread_count(self, user):
        """Get the number of unread messages for a user"""
        participant = self.participants.filter(user=user).first()
        if not participant:
            return 0
        
        last_read = participant.last_read
        if not last_read:
            return self.messages.count()
        
        return self.messages.filter(timestamp__gt=last_read).count()
    
    def mark_as_read(self, user):
        """Mark all messages in the conversation as read for a user"""
        participant = self.participants.filter(user=user).first()
        if participant:
            participant.last_read = timezone.now()
            participant.save()
            
            # Also mark messages as read
            self.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)
    
    def is_participant(self, user):
        """Check if a user is a participant in this conversation"""
        return self.participants.filter(user=user, is_active=True).exists()
    
    def is_admin(self, user):
        """Check if a user is an admin in this conversation"""
        return self.participants.filter(user=user, is_admin=True, is_active=True).exists()


class Participant(models.Model):
    """
    Participant in a conversation
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    joined_at = models.DateTimeField(_('Joined At'), auto_now_add=True)
    is_admin = models.BooleanField(_('Admin'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    last_read = models.DateTimeField(_('Last Read'), null=True, blank=True)
    has_unread = models.BooleanField(_('Has Unread Messages'), default=False)
    
    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        unique_together = ('conversation', 'user')
    
    def __str__(self):
        return f"{self.user} in {self.conversation}"
    
    def mark_as_read(self):
        """Mark this participant as having read the conversation up to now"""
        self.last_read = timezone.now()
        self.has_unread = False
        self.save()
        
        # Also mark messages as read
        self.conversation.messages.filter(is_read=False).exclude(sender=self.user).update(is_read=True)


class Message(models.Model):
    """
    Individual message in a conversation
    """
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_messages')
    content = models.TextField(_('Content'))
    timestamp = models.DateTimeField(_('Timestamp'), default=timezone.now)
    is_read = models.BooleanField(_('Read'), default=False)
    
    # For media attachments
    attachment = models.FileField(_('Attachment'), upload_to='message_attachments/', blank=True, null=True)
    attachment_type = models.CharField(_('Attachment Type'), max_length=20, blank=True)
    
    # For message status
    is_edited = models.BooleanField(_('Edited'), default=False)
    is_deleted = models.BooleanField(_('Deleted'), default=False)
    edited_at = models.DateTimeField(_('Edited At'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['timestamp']
    
    def __str__(self):
        if self.is_deleted:
            return f"Deleted message from {self.sender} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        return f"Message from {self.sender} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        """Override save to handle attachment types and conversation timestamp update"""
        # Determine attachment type if there's an attachment
        if self.attachment and not self.attachment_type:
            from .utils import determine_file_type
            self.attachment_type = determine_file_type(self.attachment)
        
        # Save the message
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update the conversation's last_message_at timestamp
        if is_new:
            self.conversation.last_message_at = self.timestamp
            self.conversation.save(update_fields=['last_message_at'])
            
            # Mark as unread for all participants except sender
            Participant.objects.filter(
                conversation=self.conversation
            ).exclude(
                user=self.sender
            ).update(
                has_unread=True
            )
    
    def edit_message(self, new_content):
        """Edit a message"""
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()
        return self
    
    def delete_message(self):
        """Soft delete a message"""
        self.is_deleted = True
        self.content = "This message has been deleted"
        if self.attachment:
            # If we want to delete the actual file, we could do it here
            self.attachment = None
            self.attachment_type = ""
        self.save()
        return self
    
    def mark_as_read(self):
        """Mark this message as read"""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
        return self
    
    def get_attachment_url(self):
        """Get the URL of the attachment, if it exists"""
        if self.attachment:
            return self.attachment.url
        return None
    
    def get_sender_display(self):
        """Get a display name for the sender"""
        if not self.sender:
            return "Unknown User"
        
        if self.sender.first_name and self.sender.last_name:
            return f"{self.sender.first_name} {self.sender.last_name}"
        
        return self.sender.username
    
    @property
    def has_attachment(self):
        """Check if this message has an attachment"""
        return bool(self.attachment)