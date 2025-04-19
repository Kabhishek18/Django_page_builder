from django.conf import settings
from .models import Theme, ThemeOption


def theme_context(request):
    """
    Context processor that adds theme-related context to all templates
    """
    context = {}
    
    try:
        # Get active theme
        active_theme = Theme.objects.filter(is_active=True).first()
        
        if active_theme:
            context['theme'] = active_theme
            
            # Get all theme options
            theme_options = {}
            for option in ThemeOption.objects.filter(theme=active_theme):
                theme_options[option.key] = option.get_value()
                
            context['theme_options'] = theme_options
            
            # Add theme paths
            context['theme_template_dir'] = f"themes/{active_theme.directory}"
            
            if active_theme.css_file:
                context['theme_css'] = active_theme.css_file
            
            if active_theme.js_file:
                context['theme_js'] = active_theme.js_file
    except:
        # If there's any error, use default theme settings
        context['theme'] = None
        context['theme_options'] = {}
        context['theme_template_dir'] = ""
    
    return context