# jitsi/urls.py
from django.urls import path
from . import views

app_name = 'jitsi'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('rooms/create/', views.create_room, name='create_room'),
    path('rooms/<uuid:room_id>/join/', views.join_meeting, name='join_meeting'),
    path('rooms/<uuid:room_id>/end/', views.end_meeting, name='end_meeting'),
    path('rooms/<uuid:room_id>/', views.room_detail, name='room_detail'),
    path('join/', views.join_meeting_landing, name='join_meeting_landing'),
    path('rooms/<uuid:room_id>/customize/', views.customize_meeting, name='customize_meeting'),
]
