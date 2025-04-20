# jitsi/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    JitsiRoom, JitsiParticipant, JitsiCustomization, 
    JitsiFeatureConfig, JitsiMeeting
)


class JitsiParticipantInline(admin.TabularInline):
    model = JitsiParticipant
    extra = 0
    readonly_fields = ['joined_at', 'left_at']


@admin.register(JitsiRoom)
class JitsiRoomAdmin(admin.ModelAdmin):
    list_display = ['name', 'creator', 'status', 'scheduled_at', 'ended_at', 'is_public']
    list_filter = ['status', 'is_public', 'created_at', 'scheduled_at']
    search_fields = ['name', 'description', 'creator__username', 'creator__email']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'scheduled_at'
    inlines = [JitsiParticipantInline]
    fieldsets = (
        ('Room Information', {
            'fields': ('id', 'name', 'slug', 'description', 'creator', 'status')
        }),
        ('Scheduling', {
            'fields': ('created_at', 'scheduled_at', 'ended_at')
        }),
        ('Access Control', {
            'fields': ('is_public', 'password_protected', 'moderator_password', 'attendee_password')
        }),
    )


@admin.register(JitsiParticipant)
class JitsiParticipantAdmin(admin.ModelAdmin):
    list_display = ['name', 'room', 'user', 'role', 'joined_at', 'left_at']
    list_filter = ['role', 'joined_at', 'left_at']
    search_fields = ['name', 'email', 'user__username', 'room__name']
    readonly_fields = ['id', 'joined_at']
    raw_id_fields = ['user', 'room']


# jitsi/admin.py (Updated JitsiCustomizationAdmin class)

@admin.register(JitsiCustomization)
class JitsiCustomizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'preview_logo', 'created_at', 'updated_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at', 'preview_logo', 'preview_watermark']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_default')
        }),
        ('Branding', {
            'fields': ('logo', 'preview_logo', 'favicon', 'background_image', 'watermark_image', 'preview_watermark')
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color', 'background_color')
        }),
        ('Footer', {
            'fields': ('show_footer', 'footer_text')
        }),
        ('Advanced Customization', {
            'fields': ('custom_css', 'custom_js'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_logo(self, obj):
        if obj and obj.logo:
            return format_html('<img src="{}" height="50" />', obj.logo.url)
        return "No logo"
    
    def preview_watermark(self, obj):
        if obj and obj.watermark_image:
            return format_html('<img src="{}" height="30" />', obj.watermark_image.url)
        return "No watermark"
    
    preview_logo.short_description = "Logo Preview"
    preview_watermark.short_description = "Watermark Preview"

    

@admin.register(JitsiFeatureConfig)
class JitsiFeatureConfigAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'enable_audio', 'enable_video', 'enable_chat', 'enable_recording']
    list_filter = [
        'is_default', 'enable_audio', 'enable_video', 'enable_chat',
        'enable_recording', 'enable_livestreaming', 'enable_end_to_end_encryption'
    ]
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'is_default')
        }),
        ('Core Features', {
            'fields': ('enable_audio', 'enable_video', 'enable_chat', 'enable_screen_sharing')
        }),
        ('Advanced Features', {
            'fields': ('enable_recording', 'enable_livestreaming', 'enable_breakout_rooms')
        }),
        ('Security Features', {
            'fields': ('enable_lobby', 'enable_end_to_end_encryption', 'enable_password_protection')
        }),
        ('UI Features', {
            'fields': (
                'enable_reactions', 'enable_raise_hand', 'enable_tile_view',
                'enable_filmstrip', 'enable_polls', 'enable_whiteboard', 'enable_blur_background'
            )
        }),
        ('Advanced Configuration', {
            'fields': ('additional_config',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class JitsiMeetingInline(admin.TabularInline):
    model = JitsiMeeting
    extra = 0
    readonly_fields = ['started_at', 'ended_at']
    raw_id_fields = ['customization', 'feature_config']


@admin.register(JitsiMeeting)
class JitsiMeetingAdmin(admin.ModelAdmin):
    list_display = ['subject', 'meeting_id', 'room', 'started_at', 'ended_at']
    list_filter = ['created_at', 'started_at', 'ended_at']
    search_fields = ['subject', 'meeting_id', 'room__name']
    readonly_fields = ['created_at', 'started_at', 'ended_at']
    raw_id_fields = ['room', 'customization', 'feature_config']
    fieldsets = (
        ('Meeting Information', {
            'fields': ('meeting_id', 'subject', 'room')
        }),
        ('Configuration', {
            'fields': ('customization', 'feature_config')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'ended_at')
        }),
    )