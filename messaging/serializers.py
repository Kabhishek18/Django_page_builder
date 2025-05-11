# messaging/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Conversation, Participant, Message


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (minimal fields)"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    sender_username = serializers.SerializerMethodField()
    formatted_timestamp = serializers.SerializerMethodField()
    attachment_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'sender_username', 'content', 'timestamp', 
            'formatted_timestamp', 'is_read', 'is_edited', 'is_deleted', 
            'attachment', 'attachment_url', 'attachment_type'
        ]
    
    def get_sender_username(self, obj):
        return obj.sender.username if obj.sender else None
    
    def get_formatted_timestamp(self, obj):
        return obj.timestamp.strftime('%b %d, %Y, %I:%M %p')
    
    def get_attachment_url(self, obj):
        return obj.attachment.url if obj.attachment else None


class ParticipantSerializer(serializers.ModelSerializer):
    """Serializer for Participant model"""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Participant
        fields = ['id', 'user', 'is_admin', 'is_active', 'joined_at', 'last_read']


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    
    participants = ParticipantSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'name', 'type', 'creator', 'created_at', 
            'updated_at', 'last_message_at', 'description', 
            'image', 'is_active', 'participants', 'last_message',
            'unread_count'
        ]
    
    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-timestamp').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if user:
            return obj.get_unread_count(user)
        return 0


class ConversationDetailSerializer(ConversationSerializer):
    """Serializer for Conversation model with messages"""
    
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + ['messages']


# Simple serializers for responses

class MessageActionSerializer(serializers.Serializer):
    """Serializer for message action responses"""
    
    id = serializers.IntegerField()
    content = serializers.CharField(allow_blank=True)
    edited_at = serializers.DateTimeField(format='%b %d, %Y, %I:%M %p', required=False)


class MessageListSerializer(serializers.Serializer):
    """Serializer for message list response"""
    
    id = serializers.IntegerField()
    content = serializers.CharField()
    sender_id = serializers.IntegerField()
    sender_name = serializers.CharField()
    is_self = serializers.BooleanField()
    timestamp = serializers.CharField()
    is_edited = serializers.BooleanField()
    is_deleted = serializers.BooleanField()
    has_attachment = serializers.BooleanField()
    attachment_url = serializers.URLField(allow_null=True)
    attachment_type = serializers.CharField(allow_blank=True)