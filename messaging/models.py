# Step 1: Create a new 'messaging' app
# Run this command in your project directory:
# python manage.py startapp messaging

# messaging/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

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
                return f"Chat between {participants[0]} and {participants[1]}"
            else:
                return f"Private chat created on {self.created_at.strftime('%Y-%m-%d')}"
        else:
            return f"{self.get_type_display()} created on {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_participants_display(self):
        """Return a comma-separated list of participant names"""
        return ", ".join([str(p.user) for p in self.participants.all()])
    
    def add_participant(self, user, is_admin=False):
        """Add a user to this conversation"""
        participant, created = Participant.objects.get_or_create(
            conversation=self,
            user=user,
            defaults={'is_admin': is_admin}
        )
        return participant
    
    def remove_participant(self, user):
        """Remove a user from this conversation"""
        Participant.objects.filter(conversation=self, user=user).delete()
    
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
    
    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')
        unique_together = ('conversation', 'user')
    
    def __str__(self):
        return f"{self.user} in {self.conversation}"
    
    def mark_as_read(self):
        """Mark this participant as having read the conversation up to now"""
        self.last_read = timezone.now()
        self.save()


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
        return f"Message from {self.sender} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    def edit_message(self, new_content):
        """Edit a message"""
        self.content = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save()
    
    def delete_message(self):
        """Soft delete a message"""
        self.is_deleted = True
        self.content = "This message has been deleted"
        self.save()
    
    def mark_as_read(self):
        """Mark this message as read"""
        self.is_read = True
        self.save()