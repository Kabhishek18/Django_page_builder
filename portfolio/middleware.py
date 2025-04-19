from django.conf import settings
from .models import SiteSettings, MenuItem


class SiteMiddleware:
    """
    Middleware to inject site-wide context variables
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request before view is called
        response = self.get_response(request)
        # Process response after view is called
        return response

    def process_template_response(self, request, response):
        """
        Add site-wide context to template responses
        """
        # Only process if there's a context
        if hasattr(response, 'context_data'):
            # Add site settings
            try:
                site_settings = SiteSettings.objects.first()
                response.context_data['site_settings'] = site_settings
            except:
                response.context_data['site_settings'] = None
            
            # Add menus
            try:
                response.context_data['header_menu'] = MenuItem.objects.filter(
                    position__in=['header', 'header_footer'],
                    parent__isnull=True,
                    is_active=True
                ).order_by('order')
                
                response.context_data['footer_menu'] = MenuItem.objects.filter(
                    position__in=['footer', 'header_footer'],
                    parent__isnull=True,
                    is_active=True
                ).order_by('order')
                
                response.context_data['sidebar_menu'] = MenuItem.objects.filter(
                    position='sidebar',
                    parent__isnull=True,
                    is_active=True
                ).order_by('order')
            except:
                # If there's an error, set them to empty
                response.context_data['header_menu'] = []
                response.context_data['footer_menu'] = []
                response.context_data['sidebar_menu'] = []
            
            # Add theme context
            try:
                from themes.models import Theme
                active_theme = Theme.objects.filter(is_active=True).first()
                response.context_data['active_theme'] = active_theme
            except:
                response.context_data['active_theme'] = None
                
        return response