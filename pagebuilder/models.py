from django.db import models

# Create your models here.
from django.db import models
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField
from colorfield.fields import ColorField
import json, os

class Page(models.Model):
    """
    Represents a dynamic webpage on the website (e.g., Home, About Us, Services).
    This is the top-level unit that brings together layout, SEO, navigation, and content blocks.
    """
    # Basic page information
    title = models.CharField(_('Title'), max_length=200, help_text=_('Page title shown in browser tab and headings'))
    slug = models.SlugField(_('Slug'), max_length=200, unique=True, help_text=_('URL-safe identifier (e.g., /about-us)'))
    url_override = models.CharField(_('URL Override'), max_length=255, blank=True, null=True, 
                                   help_text=_('Custom URL if needed (leave blank to use slug)'))
    
    # Page status and visibility
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_homepage = models.BooleanField(_('Is Homepage'), default=False)
    
    # Timestamps for lifecycle management
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    publish_date = models.DateTimeField(_('Publish Date'), null=True, blank=True)
    
    # Navigation information
    MENU_PLACEMENT_CHOICES = (
        ('none', _('None')),
        ('header', _('Header')),
        ('footer', _('Footer')),
        ('sidebar', _('Sidebar')),
        ('header_footer', _('Header & Footer')),
    )
    menu_placement = models.CharField(_('Menu Placement'), max_length=20, choices=MENU_PLACEMENT_CHOICES, default='none')
    menu_label = models.CharField(_('Menu Label'), max_length=100, blank=True, 
                                 help_text=_('Display label for navigation menus (defaults to page title if empty)'))
    parent = models.ForeignKey('self', verbose_name=_('Parent Page'), on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='children')
    order = models.IntegerField(_('Order'), default=0, help_text=_('Order of the page in menus'))
    
    # Page metadata & controls
    author = models.ForeignKey(User, verbose_name=_('Author'), on_delete=models.SET_NULL, null=True)
    custom_css_class = models.CharField(_('Custom CSS Class'), max_length=100, blank=True)
    
    BACKGROUND_THEME_CHOICES = (
        ('light', _('Light')),
        ('dark', _('Dark')),
        ('custom', _('Custom')),
    )
    background_theme = models.CharField(_('Background Theme'), max_length=20, 
                                       choices=BACKGROUND_THEME_CHOICES, default='light')
    background_color = ColorField(_('Background Color'), blank=True, null=True)
    
    language = models.CharField(_('Language'), max_length=10, default='en')
    page_settings_json = models.JSONField(_('Page Settings'), default=dict, blank=True)
    
    # SEO & OpenGraph (Social Sharing)
    meta_title = models.CharField(_('Meta Title'), max_length=100, blank=True,
                                 help_text=_('Custom title for search engine (defaults to page title if empty)'))
    meta_description = models.TextField(_('Meta Description'), blank=True,
                                       help_text=_('Summary shown in search results'))
    meta_keywords = models.TextField(_('Meta Keywords'), blank=True,
                                    help_text=_('(Legacy) keywords for search'))
    og_title = models.CharField(_('OG Title'), max_length=100, blank=True,
                               help_text=_('Facebook/Twitter preview title'))
    og_description = models.TextField(_('OG Description'), blank=True,
                                     help_text=_('Social media preview text'))
    og_image = models.ImageField(_('OG Image'), upload_to='og_images/', blank=True, null=True,
                                help_text=_('Image shown when the link is shared'))
    canonical_url = models.URLField(_('Canonical URL'), blank=True,
                                   help_text=_('To prevent duplicate content SEO issues'))

    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['order', 'title']

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
            
        # If this is set as homepage, unset any other homepage
        if self.is_homepage:
            # Get current homepage(s) excluding this page
            Page.objects.filter(is_homepage=True).exclude(pk=self.pk).update(is_homepage=False)
            
        # Default menu_label to title if not provided
        if not self.menu_label:
            self.menu_label = self.title
            
        # Default meta_title to title if not provided
        if not self.meta_title:
            self.meta_title = self.title
            
        super(Page, self).save(*args, **kwargs)
        
    def get_absolute_url(self):
        if self.url_override:
            return self.url_override
        elif self.is_homepage:
            return reverse('home')
        else:
            return reverse('page_detail', kwargs={'slug': self.slug})

    def get_blocks(self):
        """Get all blocks for this page in the correct order"""
        return self.blocks.filter(is_active=True).order_by('position')
        
    def get_page_settings(self):
        """Parse page settings JSON into a Python dictionary"""
        if not self.page_settings_json:
            return {}
            
        if isinstance(self.page_settings_json, str):
            try:
                return json.loads(self.page_settings_json)
            except Exception:
                return {}
        return self.page_settings_json



def get_available_templates():
    """Returns a list of available block templates for selection"""
    try:
        # Try to get templates from the Template model if it exists
        from themes.models import Template
        template_choices = [
            (template.slug, template.name) 
            for template in Template.objects.filter(type='block')
        ]
        
        # Also scan the template directories for HTML files
        block_dir = os.path.join(settings.BASE_DIR, 'templates', 'blocks')
        if os.path.exists(block_dir):
            for file in os.listdir(block_dir):
                if file.endswith('.html'):
                    template_name = file[:-5]  # Remove .html
                    # Don't add if already in the list
                    if not any(template_name == slug for slug, _ in template_choices):
                        display_name = template_name.replace('_', ' ').title()
                        template_choices.append((template_name, display_name))
        
        return template_choices
    except (ImportError, ModuleNotFoundError):
        # If Template model doesn't exist, just scan directories
        block_dir = os.path.join(settings.BASE_DIR, 'templates', 'blocks')
        template_choices = []
        
        if os.path.exists(block_dir):
            for file in os.listdir(block_dir):
                if file.endswith('.html'):
                    template_name = file[:-5]  # Remove .html
                    display_name = template_name.replace('_', ' ').title()
                    template_choices.append((template_name, display_name))
        
        return template_choices

class Block(models.Model):
    """
    Represents a modular section of a page, such as hero sections, testimonials,
    galleries, or even custom HTML.
    """
    # Basic block information
    page = models.ForeignKey(Page, verbose_name=_('Page'), related_name='blocks', on_delete=models.CASCADE)
    label = models.CharField(_('Label'), max_length=100, help_text=_('Admin-friendly name (e.g., "Hero Section")'))
    position = models.PositiveIntegerField(_('Position'), default=0)
    is_active = models.BooleanField(_('Active'), default=True)
    
    # Block type and content
    BLOCK_TYPE_CHOICES = (
        ('template', _('Template')),
        ('html', _('Raw HTML')),
        ('wysiwyg', _('WYSIWYG Editor')),
    )
    type = models.CharField(_('Type'), max_length=20, choices=BLOCK_TYPE_CHOICES, default='template')
    template_name = models.CharField(
        _('Template Name'), 
        max_length=100, 
        blank=True,
        choices=get_available_templates,
        help_text=_('Select which template to use if type is template')
    )
    
    # Content fields for different block types
    html_content = models.TextField(_('HTML Content'), blank=True,
                                  help_text=_('Raw HTML/CSS/JS content (only used if type is "html")'))
    wysiwyg_content = RichTextUploadingField(_('Rich Text Content'), blank=True,
                                           help_text=_('Visual editor content (only used if type is "wysiwyg")'))
    
    # Block settings and styling
    settings = models.JSONField(_('Settings'), default=dict, blank=True)
    custom_css = models.TextField(_('Custom CSS'), blank=True)
    css_class = models.CharField(_('CSS Class'), max_length=100, blank=True)
    background_color = ColorField(_('Background Color'), blank=True, null=True)
    text_color = ColorField(_('Text Color'), blank=True, null=True)
    padding_top = models.PositiveIntegerField(_('Padding Top (px)'), blank=True, null=True)
    padding_bottom = models.PositiveIntegerField(_('Padding Bottom (px)'), blank=True, null=True)
    padding_left = models.PositiveIntegerField(_('Padding Left (px)'), blank=True, null=True)
    padding_right = models.PositiveIntegerField(_('Padding Right (px)'), blank=True, null=True)
    
    class Meta:
        verbose_name = _('Block')
        verbose_name_plural = _('Blocks')
        ordering = ['page', 'position']

    def __str__(self):
        return f"{self.label} ({self.get_type_display()}) - {self.page.title}"
        
    def get_content(self):
        """Returns the appropriate content based on block type"""
        if self.type == 'html':
            return self.html_content
        elif self.type == 'wysiwyg':
            return self.wysiwyg_content
        else:
            return None
            
    def get_template(self):
        """Get the template path to render this block"""
        if self.type == 'template' and self.template_name:
            return f"blocks/{self.template_name}.html"
        elif self.type == 'wysiwyg':
            return "blocks/wysiwyg.html"
        elif self.type == 'html':
            return "blocks/raw_html.html"
        else:
            return "blocks/default.html"
            
    def get_settings(self):
        """Parse block settings JSON into a Python dictionary"""
        if not self.settings:
            return {}
            
        if isinstance(self.settings, str):
            try:
                return json.loads(self.settings)
            except Exception:
                return {}
        return self.settings
        
    def get_style(self):
        """Generate inline CSS style based on block settings"""
        style = ""
        if self.background_color:
            style += f"background-color: {self.background_color}; "
        if self.text_color:
            style += f"color: {self.text_color}; "
        if self.padding_top is not None:
            style += f"padding-top: {self.padding_top}px; "
        if self.padding_bottom is not None:
            style += f"padding-bottom: {self.padding_bottom}px; "
        if self.padding_left is not None:
            style += f"padding-left: {self.padding_left}px; "
        if self.padding_right is not None:
            style += f"padding-right: {self.padding_right}px; "
        return style.strip()