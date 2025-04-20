# jitsi/apps.py
from django.apps import AppConfig


class JitsiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jitsi'
    verbose_name = 'Jitsi Meeting Manager'
    
    def ready(self):
        # Import signals or perform other initialization
        pass