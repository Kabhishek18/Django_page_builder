from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from colorfield.fields import ColorField
import os
import json
from django.core.exceptions import ValidationError



class Theme(models.Model):
    """
    Theme model for managing website themes
    """
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True, 
                          help_text=_('Used for identifying the theme in templates'))
    description = models.TextField(_('Description'), blank=True)
    
    # Theme assets
    screenshot = models.ImageField(_('Screenshot'), upload_to='themes/', blank=True, null=True)
    directory = models.CharField(_('Template Directory'), max_length=100, 
                               help_text=_('Directory name within themes/templates/'))
    css_file = models.CharField(_('CSS File'), max_length=255, blank=True,
                              help_text=_('Path to main CSS file (relative to static folder)'))
    js_file = models.CharField(_('JS File'), max_length=255, blank=True,
                             help_text=_('Path to main JS file (relative to static folder)'))
    
    # Theme status
    is_active = models.BooleanField(_('Active'), default=False)
    is_system = models.BooleanField(_('System Theme'), default=False,
                                  help_text=_('System themes cannot be deleted'))
    
    # Theme metadata
    author = models.CharField(_('Author'), max_length=100, blank=True)
    version = models.CharField(_('Version'), max_length=20, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    # Theme configuration
    supports_blocks = models.BooleanField(_('Supports Block Editor'), default=True)
    supports_dark_mode = models.BooleanField(_('Supports Dark Mode'), default=False)
    supports_responsive = models.BooleanField(_('Supports Responsive Design'), default=True)
    
    class Meta:
        verbose_name = _('Theme')
        verbose_name_plural = _('Themes')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # If this theme is set as active, deactivate all other themes
        if self.is_active:
            Theme.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
            
        super().save(*args, **kwargs)
    
    def get_template_dir(self):
        """Returns the full path to the theme's template directory"""
        return os.path.join(settings.THEME_PATHS, self.directory)
    
    def get_available_templates(self):
        """Returns a list of available templates for this theme"""
        templates = []
        template_dir = self.get_template_dir()
        
        try:
            for root, dirs, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        # Get relative path from theme directory
                        rel_path = os.path.relpath(os.path.join(root, file), template_dir)
                        templates.append(rel_path)
        except Exception:
            # Directory might not exist yet
            pass
            
        return templates
    
    def get_block_templates(self):
        """Returns a list of available block templates for this theme"""
        block_templates = []
        template_dir = os.path.join(self.get_template_dir(), 'blocks')
        
        try:
            if os.path.exists(template_dir):
                for file in os.listdir(template_dir):
                    if file.endswith('.html'):
                        # Remove .html extension
                        template_name = file[:-5]
                        block_templates.append((template_name, template_name.replace('_', ' ').title()))
        except Exception:
            # Directory might not exist yet
            pass
            
        return block_templates


class ThemeOption(models.Model):
    """
    Theme options for customizing themes through the admin interface
    """
    theme = models.ForeignKey(Theme, verbose_name=_('Theme'), related_name='options', 
                             on_delete=models.CASCADE)
    
    name = models.CharField(_('Name'), max_length=100)
    key = models.SlugField(_('Key'), help_text=_('Used in templates to access this option'))
    value_type = models.CharField(_('Value Type'), max_length=20, choices=(
        ('text', _('Text')),
        ('textarea', _('Text Area')),
        ('number', _('Number')),
        ('boolean', _('Boolean')),
        ('color', _('Color')),
        ('image', _('Image')),
        ('select', _('Selection')),
    ), default='text')
    
    default_value = models.TextField(_('Default Value'), blank=True)
    value = models.TextField(_('Value'), blank=True)
    
    # For select type options
    choices = models.TextField(_('Choices'), blank=True, 
                             help_text=_('JSON list of choices for select type, e.g., ["Option 1", "Option 2"]'))
    
    # For image type options
    image = models.ImageField(_('Image Value'), upload_to='themes/options/', blank=True, null=True)
    
    # For color type options
    color = ColorField(_('Color Value'), blank=True, null=True)
    
    # Display settings
    label = models.CharField(_('Label'), max_length=100, 
                           help_text=_('Human-readable label shown in admin'))
    help_text = models.CharField(_('Help Text'), max_length=255, blank=True)
    required = models.BooleanField(_('Required'), default=False)
    category = models.CharField(_('Category'), max_length=100, default='General',
                              help_text=_('Used for grouping options in the admin'))
    order = models.PositiveIntegerField(_('Order'), default=0)
    
    class Meta:
        verbose_name = _('Theme Option')
        verbose_name_plural = _('Theme Options')
        ordering = ['category', 'order', 'name']
        unique_together = ('theme', 'key')
    
    def __str__(self):
        return f"{self.theme.name} - {self.name}"
    
    def get_value(self):
        """Returns the appropriate value based on value_type"""
        if not self.value and self.default_value:
            # Return default if no value set
            if self.value_type == 'color':
                return self.default_value
            elif self.value_type == 'boolean':
                return self.default_value.lower() in ('true', 'yes', '1')
            elif self.value_type == 'number':
                try:
                    return int(self.default_value)
                except (ValueError, TypeError):
                    return 0
            else:
                return self.default_value
                
        # Return value based on type
        if self.value_type == 'color':
            return self.color or self.value
        elif self.value_type == 'boolean':
            return self.value.lower() in ('true', 'yes', '1')
        elif self.value_type == 'number':
            try:
                return int(self.value)
            except (ValueError, TypeError):
                return 0
        elif self.value_type == 'image':
            return self.image.url if self.image else ''
        elif self.value_type == 'select':
            return self.value
        else:
            return self.value
    
    def get_choices(self):
        """Parse JSON choices into a list"""
        if not self.choices:
            return []
            
        try:
            return json.loads(self.choices)
        except json.JSONDecodeError:
            return [c.strip() for c in self.choices.split(',')]

class Template(models.Model):
    """Model for managing templates"""
    
    TEMPLATE_TYPE_CHOICES = (
        ('page', _('Page Template')),
        ('block', _('Block Template')),
        ('partial', _('Partial Template')),
    )
    
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), unique=True)
    type = models.CharField(_('Type'), max_length=10, choices=TEMPLATE_TYPE_CHOICES)
    description = models.TextField(_('Description'), blank=True)
    
    # The actual template content
    content = models.TextField(_('Content'))
    
    # Track metadata
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    
    class Meta:
        verbose_name = _('Template')
        verbose_name_plural = _('Templates')
        ordering = ['type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        # Save the template to the database
        super().save(*args, **kwargs)
        
        # Also save it to the file system for Django to use
        self.save_to_filesystem()
    
    def save_to_filesystem(self):
        """Save the template to the filesystem so Django can use it"""
        from django.conf import settings
        
        # Determine directory based on template type
        if self.type == 'page':
            directory = os.path.join(settings.BASE_DIR, 'templates', 'pages')
        elif self.type == 'block':
            directory = os.path.join(settings.BASE_DIR, 'templates', 'blocks')
        else:  # partial
            directory = os.path.join(settings.BASE_DIR, 'templates', 'partials')
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save the template file
        filename = f"{self.slug}.html"
        filepath = os.path.join(directory, filename)
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(self.content)            