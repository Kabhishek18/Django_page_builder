# Jitsi Integration for Portfolio Project

This module integrates Jitsi Meet video conferencing capabilities into your existing portfolio project. It allows you to create, customize, and manage video meetings directly from your Django application.

## Features

- **Meeting Management**: Create, schedule, and manage video conference rooms
- **User Roles**: Support for host, moderator, and attendee roles
- **Customization**: Brand meetings with logos, colors, and custom UI elements
- **Feature Control**: Enable/disable specific Jitsi features (recording, chat, etc.)
- **JWT Authentication**: Secure access control with JWT authentication
- **Responsive UI**: Integrates with your existing portfolio UI

## Installation and Setup

### 1. Add the App to Your Project

1. Copy the entire `jitsi` directory into your project at the same level as your other apps.

2. Add 'jitsi' to your INSTALLED_APPS in settings.py:

```python
INSTALLED_APPS = [
    # ...
    'jitsi',
    # ...
]
```

### 2. Configure Settings

Add the following settings to your `settings.py`:

```python
# Jitsi Configuration
JITSI_DOMAIN = 'meet.jit.si'  # or your self-hosted domain
JITSI_APP_ID = 'your_app_id'  # for JWT auth
JITSI_APP_SECRET = 'your_app_secret'  # for JWT auth
```

### 3. Add URLs

Include the Jitsi URLs in your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    # ...
    path('meetings/', include('jitsi.urls')),
    # ...
]
```

### 4. Run Migrations

Apply the database migrations:

```bash
python manage.py makemigrations jitsi
python manage.py migrate
```

### 5. Create Default Configurations

Create default customization and feature configurations:

```python
from django.core.management.base import BaseCommand
from jitsi.models import JitsiCustomization, JitsiFeatureConfig

class Command(BaseCommand):
    help = 'Create default Jitsi configurations'

    def handle(self, *args, **options):
        # Create default customization
        JitsiCustomization.objects.get_or_create(
            name="Default Branding",
            is_default=True,
            defaults={
                'primary_color': '#0056E0',
                'secondary_color': '#17A0DB',
                'background_color': '#040404',
                'show_footer': True,
                'footer_text': 'Powered by My Portfolio',
            }
        )
        
        # Create default feature configuration
        JitsiFeatureConfig.objects.get_or_create(
            name="Default Features",
            is_default=True,
            defaults={
                'enable_audio': True,
                'enable_video': True,
                'enable_chat': True,
                'enable_screen_sharing': True,
                'enable_recording': False,
                'enable_livestreaming': False,
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Default Jitsi configurations created successfully'))
```

Save this file as `jitsi/management/commands/create_default_jitsi_configs.py` and run:

```bash
python manage.py create_default_jitsi_configs
```

## Integration with Docker Jitsi

Your Docker Jitsi installation needs to be configured to work with this Django integration. Here are the key points:

### 1. JWT Authentication

To enable JWT authentication in your Docker Jitsi installation, update your `.env` file with the following settings:

```
# Authentication
ENABLE_AUTH=1
AUTH_TYPE=jwt
JWT_APP_ID=your_app_id  # Same as JITSI_APP_ID in Django settings
JWT_APP_SECRET=your_app_secret  # Same as JITSI_APP_SECRET in Django settings
```

### 2. Customization Integration

To allow customization from Django, you'll need to configure the external API in your Docker setup:

```
# External API
ENABLE_XMPP_WEBSOCKET=1
ENABLE_HTTP_REDIRECT=1
```

### 3. Interface Customization

Create a volume mount to allow your Django app to inject customization files:

```yaml
services:
  web:
    volumes:
      - ./interface_config.js:/config/interface_config.js
      - ./custom-css:/usr/share/jitsi-meet/css/custom-css
```

## Using the Jitsi Integration

### Creating a Meeting

1. Navigate to `/meetings/` to access the Jitsi dashboard
2. Click "Create Meeting" and fill in the details
3. Configure any advanced settings if needed
4. Save the meeting

### Customizing a Meeting

1. From the meeting detail page, click "Customize Meeting"
2. Upload logo and background images
3. Set custom colors
4. Enable/disable specific features
5. Apply the changes

### Joining a Meeting

1. From the dashboard, click "Join" on the meeting you want to attend
2. You'll be connected to the Jitsi meeting with the configured settings
3. Meeting hosts have additional controls for managing participants

## Feature Management

The integration allows you to toggle various Jitsi features:

### Core Features
- Audio & Video
- Chat
- Screen Sharing

### Advanced Features
- Recording
- Live Streaming
- Breakout Rooms
- Whiteboards
- Polls

### Security Features
- Lobby Mode
- End-to-End Encryption
- Password Protection

## UI Customization

Customize the meeting interface with:

- Logo & Branding
- Custom Background Images
- Custom Colors
- Custom CSS & JavaScript
- Footer Text

## Troubleshooting

### Common Issues

1. **JWT Authentication Errors**: Ensure your JWT_APP_ID and JWT_APP_SECRET match between Django and Jitsi Docker

2. **Missing Custom Styles**: Check that your volume mounts are correctly set up in Docker

3. **Feature Not Working**: Some features (like recording) require additional Jitsi configuration

4. **Connection Issues**: Make sure your JITSI_DOMAIN is correctly set and accessible

### Logs

Check the Django logs for connection issues and the Jitsi Docker logs for server-side problems:

```bash
# Django logs
python manage.py shell -c "from django.conf import settings; print(settings.LOGGING)"

# Docker Jitsi logs
docker-compose logs -f prosody jicofo jvb web
```

## Next Steps

After implementing this integration, consider these enhancements:

1. **Analytics Integration**: Track meeting usage and participant engagement
2. **Calendar Integration**: Sync with Google Calendar or other scheduling tools
3. **Email Notifications**: Send meeting reminders and invites
4. **Recording Management**: Store and manage meeting recordings
5. **Integration with Portfolio**: Display recent/upcoming meetings on your portfolio profile

## Technical Details

This integration uses:

- Django models for data storage
- JWT for secure authentication
- Jitsi External API for embedding
- WebSockets for real-time communication

## Contributing

If you enhance this integration, consider contributing back to the project!