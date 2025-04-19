from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField


class SiteSettings(models.Model):
    """Global settings for the portfolio site"""
    site_title = models.CharField(_('Site Title'), max_length=200)
    site_description = models.TextField(_('Site Description'), blank=True)
    site_logo = models.ImageField(_('Site Logo'), upload_to='site/', blank=True, null=True)
    site_favicon = models.ImageField(_('Site Favicon'), upload_to='site/', blank=True, null=True)
    
    # Contact information
    email = models.EmailField(_('Email'), blank=True)
    phone = models.CharField(_('Phone'), max_length=50, blank=True)
    address = models.TextField(_('Address'), blank=True)
    
    # Social links
    facebook_url = models.URLField(_('Facebook URL'), blank=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True)
    linkedin_url = models.URLField(_('LinkedIn URL'), blank=True)
    github_url = models.URLField(_('GitHub URL'), blank=True)
    youtube_url = models.URLField(_('YouTube URL'), blank=True)
    
    # Header settings
    header_background = ColorField(_('Header Background Color'), default='#ffffff')
    header_text_color = ColorField(_('Header Text Color'), default='#000000')
    
    # Footer settings
    footer_background = ColorField(_('Footer Background Color'), default='#f8f9fa')
    footer_text_color = ColorField(_('Footer Text Color'), default='#212529')
    footer_content = RichTextUploadingField(_('Footer Content'), blank=True)
    
    # Analytics
    google_analytics_id = models.CharField(_('Google Analytics ID'), max_length=50, blank=True)
    
    # SEO defaults
    default_meta_title = models.CharField(_('Default Meta Title'), max_length=100, blank=True)
    default_meta_description = models.TextField(_('Default Meta Description'), blank=True)
    default_og_image = models.ImageField(_('Default OG Image'), upload_to='site/', blank=True, null=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return self.site_title


class MenuItem(models.Model):
    """Custom menu items for header, footer or sidebar navigation"""
    POSITION_CHOICES = (
        ('header', _('Header')),
        ('footer', _('Footer')),
        ('sidebar', _('Sidebar')),
    )
    
    title = models.CharField(_('Title'), max_length=100)
    position = models.CharField(_('Position'), max_length=20, choices=POSITION_CHOICES, default='header')
    url = models.CharField(_('URL'), max_length=255)
    page = models.ForeignKey('pagebuilder.Page', verbose_name=_('Page'), 
                            on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', verbose_name=_('Parent'), 
                              on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    order = models.IntegerField(_('Order'), default=0)
    open_in_new_tab = models.BooleanField(_('Open in New Tab'), default=False)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Menu Item')
        verbose_name_plural = _('Menu Items')
        ordering = ['position', 'order']
    
    def __str__(self):
        return f"{self.title} ({self.get_position_display()})"
    
    def get_url(self):
        """Return the URL, either from direct URL or referenced page"""
        if self.page:
            return self.page.get_absolute_url()
        return self.url


class ContactMessage(models.Model):
    """Messages from contact form"""
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    subject = models.CharField(_('Subject'), max_length=200)
    message = models.TextField(_('Message'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    is_read = models.BooleanField(_('Read'), default=False)
    
    class Meta:
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name}: {self.subject} ({self.created_at.strftime('%Y-%m-%d')})"


class NewsletterSubscriber(models.Model):
    """Newsletter subscriber"""
    email = models.EmailField(_('Email'), unique=True)
    name = models.CharField(_('Name'), max_length=100, blank=True)
    subscribed_at = models.DateTimeField(_('Subscribed At'), auto_now_add=True)
    is_active = models.BooleanField(_('Active'), default=True)
    
    class Meta:
        verbose_name = _('Newsletter Subscriber')
        verbose_name_plural = _('Newsletter Subscribers')
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email