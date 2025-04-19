# templates/admin.py
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Template

@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'template_preview', 'updated_at')
    list_filter = ('type', 'created_at', 'updated_at')
    search_fields = ('name', 'slug', 'description', 'content')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'template_preview')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'type', 'description')
        }),
        (_('Template Content'), {
            'fields': ('content', 'template_preview')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def template_preview(self, obj):
        """Show a preview button for the template"""
        if obj.pk:
            return format_html(
                '<a href="{}" class="button" target="_blank">Preview</a>',
                f'/templates/preview/{obj.pk}/'
            )
        return "-"
    template_preview.short_description = _('Preview')
    
    class Media:
        css = {
            'all': ('css/codemirror.css',)
        }
        js = (
            'js/codemirror.js',
            'js/mode/htmlmixed.js',
            'js/addon/edit/matchbrackets.js',
            'js/template_admin.js',
        )