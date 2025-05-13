# messaging/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Conversation, Participant, Message


class ParticipantInline(admin.TabularInline):
    """Inline admin for participants within a conversation"""
    model = Participant
    extra = 1
    fields = ('user', 'is_admin', 'is_active', 'joined_at', 'last_read')
    readonly_fields = ('joined_at', 'last_read')


class MessageInline(admin.TabularInline):
    """Inline admin for messages within a conversation"""
    model = Message
    extra = 0
    fields = ('sender', 'content', 'timestamp', 'is_read', 'is_edited', 'is_deleted')
    readonly_fields = ('timestamp', 'is_edited', 'edited_at')
    ordering = ('-timestamp',)
    max_num = 20  # Limit the number of messages shown
    
    def has_add_permission(self, request, obj=None):
        # Admin shouldn't add messages directly
        return False


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin interface for Conversation model"""
    list_display = ('name_display', 'type', 'creator', 'participant_count', 'message_count', 'created_at', 'last_message_at')
    list_filter = ('type', 'created_at', 'is_active')
    search_fields = ('name', 'creator__username')
    readonly_fields = ('created_at', 'updated_at', 'last_message_at')
    inlines = [ParticipantInline, MessageInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'type', 'creator', 'is_active')
        }),
        (_('Details'), {
            'fields': ('description', 'image')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at', 'last_message_at'),
            'classes': ('collapse',)
        }),
    )
    
    def name_display(self, obj):
        """Return the conversation name or a default based on type"""
        if obj.name:
            return obj.name
        
        if obj.type == 'private':
            participants = obj.participants.all()[:2]
            if len(participants) == 2:
                return f"{participants[0].user} & {participants[1].user}"
        
        return f"{obj.get_type_display()} #{obj.id}"
    name_display.short_description = _('Name')
    
    def participant_count(self, obj):
        """Return the number of participants in this conversation"""
        return obj.participants.count()
    participant_count.short_description = _('Participants')
    
    def message_count(self, obj):
        """Return the number of messages in this conversation"""
        return obj.messages.count()
    message_count.short_description = _('Messages')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """Admin interface for Participant model"""
    list_display = ('user', 'conversation_link', 'is_admin', 'is_active', 'joined_at', 'last_read')
    list_filter = ('is_admin', 'is_active', 'joined_at')
    search_fields = ('user__username', 'conversation__name')
    raw_id_fields = ('user', 'conversation')
    
    def conversation_link(self, obj):
        """Link to the conversation admin"""
        url = f"/admin/messaging/conversation/{obj.conversation.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.conversation)
    conversation_link.short_description = _('Conversation')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin interface for Message model"""
    list_display = ('sender', 'conversation_link', 'content_preview', 'has_attachment', 'timestamp', 'is_read', 'is_edited', 'is_deleted')
    list_filter = ('is_read', 'is_edited', 'is_deleted', 'timestamp')
    search_fields = ('content', 'sender__username', 'conversation__name')
    readonly_fields = ('timestamp', 'edited_at')
    
    fieldsets = (
        (_('Message Details'), {
            'fields': ('conversation', 'sender', 'content', 'timestamp')
        }),
        (_('Attachment'), {
            'fields': ('attachment', 'attachment_type'),
            'classes': ('collapse',)
        }),
        (_('Status'), {
            'fields': ('is_read', 'is_edited', 'is_deleted', 'edited_at')
        }),
    )
    
    def conversation_link(self, obj):
        """Link to the conversation admin"""
        url = f"/admin/messaging/conversation/{obj.conversation.id}/change/"
        return format_html('<a href="{}">{}</a>', url, obj.conversation)
    conversation_link.short_description = _('Conversation')
    
    def content_preview(self, obj):
        """Show a preview of the message content"""
        if obj.is_deleted:
            return format_html('<span style="color: #999;">{}</span>', "This message has been deleted")
        
        # Only show first 50 characters
        preview = obj.content[:50] + ('...' if len(obj.content) > 50 else '')
        
        if obj.is_edited:
            return format_html('{} <span style="color: #999;">(edited)</span>', preview)
        return preview
    content_preview.short_description = _('Content')
    
    def has_attachment(self, obj):
        """Show if the message has an attachment"""
        return bool(obj.attachment)
    has_attachment.boolean = True
    has_attachment.short_description = _('Attachment')