from django.contrib.admin import AdminSite
from django.contrib.admin.apps import AdminConfig
from django.utils.translation import gettext_lazy as _


class KabhishekAdminSite(AdminSite):
    """Custom admin site for Kabhishek18 Portfolio"""
    
    # Customize admin site title, header, and index title
    site_title = _('Kabhishek18 Portfolio')
    site_header = _('Kabhishek18 Portfolio Admin')
    index_title = _('Dashboard')
    
    def get_app_list(self, request, app_label=None):
        """Customize the admin sidebar to group apps in a more user-friendly way"""
        app_list = super().get_app_list(request, app_label)
        
        # Define custom groupings with priority order
        custom_ordering = {
            'Content': ['pagebuilder.page', 'pagebuilder.block'],
            'Media': ['media.mediaitem', 'media.mediafolder'],
            'Appearance': ['themes.theme', 'themes.themeoption'],
            'Settings': ['auth.user', 'auth.group'],
        }
        
        # Create a new ordered app list
        ordered_app_list = []
        
        # Add the custom groups first
        for group_name, models in custom_ordering.items():
            group_dict = {
                'name': group_name,
                'app_label': group_name.lower(),
                'app_url': '#',
                'has_module_perms': True,
                'models': [],
            }
            
            # Find and group models according to the custom ordering
            for app_dict in app_list:
                for model_dict in app_dict['models']:
                    model_name = f"{app_dict['app_label']}.{model_dict['object_name'].lower()}"
                    if model_name in models:
                        model_copy = model_dict.copy()
                        group_dict['models'].append(model_copy)
            
            if group_dict['models']:
                ordered_app_list.append(group_dict)
        
        # Add remaining apps that are not in the custom ordering
        for app_dict in app_list:
            should_include = True
            for group_dict in ordered_app_list:
                for model_dict in group_dict['models']:
                    if (model_dict['object_name'].lower() in 
                        [m['object_name'].lower() for m in app_dict['models']]):
                        should_include = False
                        break
                if not should_include:
                    break
                    
            if should_include and app_dict['models']:
                ordered_app_list.append(app_dict)
        
        return ordered_app_list


class KabhishekAdminConfig(AdminConfig):
    """Custom admin configuration that uses our custom AdminSite"""
    default_site = 'core.admin.KabhishekAdminSite'