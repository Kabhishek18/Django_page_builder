from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.db import models
from django.forms import TextInput, Select, Textarea
from .models import Page, Block, get_available_templates
from django import forms  

# Fix pagebuilder/admin.py to handle the template_name field properly

class BlockInline(admin.StackedInline):
    """Inline editor for blocks within a page"""
    model = Block
    extra = 0
    fieldsets = (
        (_('Block Info'), {
            'fields': ('label', 'position', 'is_active'),
        }),
        (_('Content'), {
            'fields': ('type', 'template_name', 'html_content', 'wysiwyg_content'),
            'classes': ('collapse',),
        }),
        (_('Styling'), {
            'fields': ('css_class', 'background_color', 'text_color',
                      'padding_top', 'padding_bottom', 'padding_left', 'padding_right'),
            'classes': ('collapse',),
        }),
        (_('Advanced'), {
            'fields': ('settings', 'custom_css'),
            'classes': ('collapse',),
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '40'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    
    def get_formset(self, request, obj=None, **kwargs):
        """Dynamically show/hide fields based on block type"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Fix the media class
        formset.media = forms.Media(
            js=['js/block_admin.js'],
        )
        
        return formset
        
    def formfield_for_dbfield(self, db_field, **kwargs):
        """Customize the form fields"""
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        
        if db_field.name == 'template_name':
            # Refresh template choices every time
            choices = get_available_templates()
            
            # Add a preview image option if exists
            formfield.widget = forms.Select(
                choices=choices,
                attrs={'class': 'template-select'}
            )
            
        return formfield


class BlockAdmin(admin.ModelAdmin):
    """Standalone admin for blocks"""
    list_display = ('label', 'page_link', 'type', 'position', 'is_active')
    list_filter = ('type', 'is_active', 'page')
    search_fields = ('label', 'page__title')
    ordering = ('page', 'position')
    
    fieldsets = (
        (_('Block Info'), {
            'fields': ('page', 'label', 'position', 'is_active'),
        }),
        (_('Content'), {
            'fields': ('type', 'template_name', 'html_content', 'wysiwyg_content'),
        }),
        (_('Styling'), {
            'fields': ('css_class', 'background_color', 'text_color',
                      'padding_top', 'padding_bottom', 'padding_left', 'padding_right'),
            'classes': ('collapse',),
        }),
        (_('Advanced'), {
            'fields': ('settings', 'custom_css'),
            'classes': ('collapse',),
        }),
    )
    
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '60'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 8, 'cols': 80})},
    }
    
    def page_link(self, obj):
        """Creates a link to the page admin"""
        if obj.page:
            url = reverse('admin:pagebuilder_page_change', args=[obj.page.id])
            return format_html('<a href="{}">{}</a>', url, obj.page.title)
        return "-"
    page_link.short_description = _('Page')
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        """Customize the form fields"""
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        
        if db_field.name == 'template_name':
            # Refresh template choices every time
            choices = get_available_templates()
            
            # Add a preview image option if exists
            formfield.widget = forms.Select(
                choices=choices,
                attrs={'class': 'template-select'}
            )
            
        return formfield
    
    class Media:
        js = ('js/block_admin.js',)
        

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    """Admin interface for Page model with intuitive organization"""
    list_display = ('title', 'status', 'url_display', 'menu_placement', 'is_homepage', 'created_at', 'updated_at')
    list_filter = ('status', 'menu_placement', 'is_homepage', 'background_theme')
    search_fields = ('title', 'slug', 'meta_title', 'meta_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BlockInline]
    save_on_top = True
    
    def url_display(self, obj):
        """Format the URL for display and link to the actual page"""
        if obj.status == 'published':
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        else:
            return obj.slug
    url_display.short_description = _('URL')
    
    # Organize fields into logical panels
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'status', 'is_homepage', 'author', 'publish_date'),
        }),
        (_('Navigation'), {
            'fields': ('menu_placement', 'menu_label', 'parent', 'order', 'url_override'),
            'classes': ('collapse',),
        }),
        (_('Design'), {
            'fields': ('background_theme', 'background_color', 'custom_css_class'),
            'classes': ('collapse',),
        }),
        (_('SEO & Social Media'), {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 
                       'og_title', 'og_description', 'og_image', 'canonical_url'),
            'classes': ('collapse',),
        }),
        (_('Advanced'), {
            'fields': ('language', 'page_settings_json'),
            'classes': ('collapse',),
        }),
    )
    
    # Custom form widgets
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '60'})},
        models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 80})},
    }
    
    def save_model(self, request, obj, form, change):
        """Set the author automatically if not already set"""
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'author' in form.base_fields:
            form.base_fields['author'].initial = request.user
        return form
    
    class Media:
        css = {
            'all': ('css/page_admin.css',)
        }
        js = ('js/page_admin.js',)


# Register standalone Block admin
admin.site.register(Block, BlockAdmin)