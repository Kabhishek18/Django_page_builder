# In pagebuilder/views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.conf import settings

@staff_member_required
def preview_template(request, template_name):
    """Preview a block template in the admin"""
    # Check if template exists
    template_path = os.path.join(settings.BASE_DIR, 'templates', 'blocks', f"{template_name}.html")
    
    if os.path.exists(template_path):
        # Read the template file
        with open(template_path, 'r') as f:
            template_content = f.read()
            
        # Return a simple preview
        return render(request, 'pagebuilder/template_preview.html', {
            'template_name': template_name,
            'template_content': template_content,
        })
    else:
        return HttpResponse("Template not found")