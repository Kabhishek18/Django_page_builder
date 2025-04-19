from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import SiteSettings, MenuItem, ContactMessage, NewsletterSubscriber


class SingletonModelAdmin(admin.ModelAdmin):
    """
    Admin for singleton models (only one instance allowed)
    """
    def has_add_permission(self, request):
        # Check if an instance already exists
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton instance
        return False


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    """Admin interface for site settings"""
    fieldsets = (
        (_('Site Information'), {
            'fields': ('site_title', 'site_description', 'site_logo', 'site_favicon')
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'address')
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 
                      'linkedin_url', 'github_url', 'youtube_url')
        }),
        (_('Header & Footer'), {
            'fields': ('header_background', 'header_text_color', 
                      'footer_background', 'footer_text_color', 'footer_content')
        }),
        (_('Analytics & SEO'), {
            'fields': ('google_analytics_id', 'default_meta_title', 
                      'default_meta_description', 'default_og_image')
        }),
    )
    
    def get_changelist_instance(self, request):
        """Override to automatically redirect to the single instance"""
        if self.model.objects.exists():
            instance = self.model.objects.first()
            return self.model.objects.filter(pk=instance.pk)
        return super().get_changelist_instance(request)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    """Admin interface for menu items"""
    list_display = ('title', 'position', 'url_or_page', 'parent', 'order', 'is_active')
    list_filter = ('position', 'is_active')
    search_fields = ('title', 'url')
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        (_('Menu Item Information'), {
            'fields': ('title', 'position', 'parent', 'order', 'is_active')
        }),
        (_('Target'), {
            'fields': ('url', 'page', 'open_in_new_tab'),
            'description': _('Specify either a URL or select a page (page takes precedence if both are provided)')
        }),
    )
    
    def url_or_page(self, obj):
        """Display URL or page reference"""
        if obj.page:
            page_url = obj.page.get_absolute_url()
            return format_html('<a href="{}">{}</a> (Page)', page_url, page_url)
        return format_html('<a href="{}">{}</a>', obj.url, obj.url)
    url_or_page.short_description = _('URL')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin interface for contact messages"""
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')
    
    def has_add_permission(self, request):
        # Prevent adding new contact messages through admin
        return False


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    """Admin interface for newsletter subscribers"""
    list_display = ('email', 'name', 'subscribed_at', 'is_active')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email', 'name')
    list_editable = ('is_active',)
    
    def get_readonly_fields(self, request, obj=None):
        # Make email and subscribed_at readonly when editing
        if obj:
            return ('email', 'subscribed_at')
        return ()