# messaging/urls.py
from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Main inbox view
    path('', views.inbox, name='inbox'),
    
    # Conversation views
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('conversation/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('conversation/<int:conversation_id>/messages/', views.load_messages, name='load_messages'),
    path('conversation/<int:conversation_id>/mark-read/', views.mark_as_read, name='mark_as_read'),
    
    # Message actions
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
    
    # Create new conversations
    path('new/private/', views.new_private_conversation, name='new_private_conversation'),
    path('new/group/', views.new_group_conversation, name='new_group_conversation'),
    path('new/broadcast/', views.new_broadcast, name='new_broadcast'),
    
    # Group conversation management
    path('group/<int:conversation_id>/manage/', views.manage_group, name='manage_group'),
    path('group/<int:conversation_id>/add-member/', views.add_group_member, name='add_group_member'),
    path('group/<int:conversation_id>/remove-member/<int:user_id>/', views.remove_group_member, name='remove_group_member'),
    path('group/<int:conversation_id>/leave/', views.leave_group, name='leave_group'),
    
    # Notifications and updates
    path('notifications/', views.message_notifications, name='message_notifications'),
    path('unread-count/', views.unread_count, name='unread_count'),
]