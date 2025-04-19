# templates/views.py (additional view)
@staff_member_required
def template_dashboard(request):
    """Template management dashboard"""
    templates = Template.objects.all()
    
    page_templates = templates.filter(type='page')
    block_templates = templates.filter(type='block')
    partial_templates = templates.filter(type='partial')
    
    return render(request, 'templates/dashboard.html', {
        'page_templates': page_templates,
        'block_templates': block_templates,
        'partial_templates': partial_templates,
    })