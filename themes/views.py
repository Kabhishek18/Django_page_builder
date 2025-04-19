from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.template import Template as DjangoTemplate, Context
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Template

@staff_member_required
def template_dashboard(request):
    """Template management dashboard"""
    templates = Template.objects.all()
    
    page_templates = templates.filter(type='page')
    block_templates = templates.filter(type='block')
    partial_templates = templates.filter(type='partial')
    
    return render(request, 'themes/dashboard.html', {
        'page_templates': page_templates,
        'block_templates': block_templates,
        'partial_templates': partial_templates,
    })

@staff_member_required
def preview_template(request, template_id):
    """Preview a template with sample data"""
    template = get_object_or_404(Template, pk=template_id)
    
    # Create sample data based on template type
    sample_data = {}
    if template.type == 'page':
        sample_data = {
            'page': {
                'title': 'Sample Page',
                'content': 'This is sample content for preview.',
                'meta_title': 'Sample Page Title',
                'meta_description': 'Sample meta description',
            },
            'blocks': []
        }
    elif template.type == 'block':
        sample_data = {
            'block': {
                'id': 1,
                'label': 'Sample Block',
                'css_class': 'sample-block',
                'position': 1,
                'get_style': 'background-color: #f5f5f5; padding: 20px;',
                'content': 'This is sample block content for preview.',
            }
        }
    
    # Render the template with sample data
    django_template = DjangoTemplate(template.content)
    html = django_template.render(Context(sample_data))
    
    return render(request, 'themes/preview.html', {
        'template': template,
        'html': html,
        'raw_template': template.content,
    })

@staff_member_required
def create_template(request):
    """Create a new template"""
    if request.method == 'POST':
        # Handle template creation logic
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        template_type = request.POST.get('type')
        description = request.POST.get('description')
        content = request.POST.get('content')
        
        template = Template(
            name=name,
            slug=slug,
            type=template_type,
            description=description,
            content=content
        )
        
        try:
            template.save()
            messages.success(request, _('Template created successfully.'))
            return redirect('themes:dashboard')
        except Exception as e:
            messages.error(request, _(f'Error creating template: {str(e)}'))
    
    # GET request - show the creation form
    template_type = request.GET.get('type', 'page')
    
    return render(request, 'themes/create_template.html', {
        'template_type': template_type,
    })

@staff_member_required
def edit_template(request, template_id):
    """Edit an existing template"""
    template = get_object_or_404(Template, pk=template_id)
    
    if request.method == 'POST':
        # Handle template update logic
        template.name = request.POST.get('name')
        template.slug = request.POST.get('slug')
        template.type = request.POST.get('type')
        template.description = request.POST.get('description')
        template.content = request.POST.get('content')
        
        try:
            template.save()
            messages.success(request, _('Template updated successfully.'))
            return redirect('themes:dashboard')
        except Exception as e:
            messages.error(request, _(f'Error updating template: {str(e)}'))
    
    return render(request, 'themes/edit_template.html', {
        'template': template,
    })

@staff_member_required
def delete_template(request, template_id):
    """Delete a template"""
    template = get_object_or_404(Template, pk=template_id)
    
    if request.method == 'POST':
        try:
            template.delete()
            messages.success(request, _('Template deleted successfully.'))
        except Exception as e:
            messages.error(request, _(f'Error deleting template: {str(e)}'))
        
        return redirect('themes:dashboard')
    
    return render(request, 'themes/delete_template.html', {
        'template': template,
    })

@staff_member_required
def import_template(request):
    """Import a template from file"""
    if request.method == 'POST' and request.FILES.get('template_file'):
        try:
            template_file = request.FILES['template_file']
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            template_type = request.POST.get('type')
            description = request.POST.get('description')
            
            # Read content from uploaded file
            content = template_file.read().decode('utf-8')
            
            template = Template(
                name=name,
                slug=slug,
                type=template_type,
                description=description,
                content=content
            )
            
            template.save()
            messages.success(request, _('Template imported successfully.'))
            return redirect('themes:dashboard')
        except Exception as e:
            messages.error(request, _(f'Error importing template: {str(e)}'))
    
    return render(request, 'themes/import_template.html')

@staff_member_required
def export_template(request, template_id):
    """Export a template as a file"""
    template = get_object_or_404(Template, pk=template_id)
    
    response = HttpResponse(template.content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="{template.slug}.html"'
    
    return response