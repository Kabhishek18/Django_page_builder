# Jitsi Docker Integration Guide

This guide will help you connect your existing Docker Jitsi installation with the Django integration app.

## 1. Configuring Your Existing Docker Jitsi

### JWT Authentication Setup

To enable JWT authentication in your Docker Jitsi installation:

1. Edit the `.env` file in your Jitsi Docker directory:

```
# Authentication
ENABLE_AUTH=1
AUTH_TYPE=jwt
# Replace with values that match your Django settings
JWT_APP_ID=your_app_id
JWT_APP_SECRET=your_app_secret
JWT_ACCEPTED_ISSUERS=["your_app_id"]
JWT_ACCEPTED_AUDIENCES=["jitsi"]
```

2. Restart your Jitsi containers:

```bash
docker-compose down
docker-compose up -d
```

### Custom Interface Configuration

To enable custom branding:

1. Create an `interface_config.js` file in your Jitsi Docker directory:

```javascript
/* eslint-disable no-unused-vars, no-var */

var interfaceConfig = {
    APP_NAME: 'My Portfolio Meetings',
    DEFAULT_BACKGROUND: '#040404',
    DEFAULT_LOGO_URL: '/images/logo.png', // This will be overridden by Django
    DEFAULT_WELCOME_PAGE_LOGO_URL: '/images/logo.png',
    DISABLE_VIDEO_BACKGROUND: false,
    DISPLAY_WELCOME_FOOTER: false,
    JITSI_WATERMARK_LINK: '',
    SHOW_CHROME_EXTENSION_BANNER: false,
    SHOW_JITSI_WATERMARK: true,
    TOOLBAR_BUTTONS: [
        'microphone', 'camera', 'desktop', 'fullscreen',
        'fodeviceselection', 'hangup', 'profile', 'chat',
        'recording', 'livestreaming', 'etherpad',
        'sharedvideo', 'settings', 'raisehand',
        'videoquality', 'filmstrip', 'invite',
        'feedback', 'stats', 'shortcuts',
        'tileview', 'videobackgroundblur', 'download',
        'help', 'mute-everyone', 'security'
    ],
};
```

2. Update your `docker-compose.yml` to mount this file:

```yaml
services:
  web:
    volumes:
      - ./interface_config.js:/usr/share/jitsi-meet/interface_config.js
      - ./branding:/usr/share/jitsi-meet/images/custom
```

3. Create a directory for custom branding:

```bash
mkdir -p branding
```

## 2. Django Project Configuration

### Settings Configuration

1. Add the following settings to your Django project's `settings.py`:

```python
# Jitsi Configuration
JITSI_DOMAIN = 'your-jitsi-domain.com'  # Your Docker Jitsi domain
JITSI_APP_ID = 'your_app_id'  # Must match JWT_APP_ID in Docker .env
JITSI_APP_SECRET = 'your_app_secret'  # Must match JWT_APP_SECRET in Docker .env

# Media settings for Jitsi customization files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_files')

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ...
    'jitsi',
    # ...
]
```

2. Update your main `urls.py` file:

```python
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # ...
    path('meetings/', include('jitsi.urls')),
    # ...
]

# Add media serving for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## 3. Testing the Integration

1. Start your Django server:

```bash
python manage.py runserver
```

2. Create the default Jitsi configurations:

```bash
python manage.py create_default_jitsi_configs
```

3. Navigate to `/meetings/` in your browser

4. Create a test meeting and verify it connects to your Docker Jitsi instance

## 4. Customization Workflow

When a user uploads a logo or customizes the Jitsi interface in Django:

1. The files are saved to `MEDIA_ROOT/jitsi/`
2. The Django app generates config with URLs pointing to these files
3. When a meeting is joined, these configs are passed to the Jitsi iframe API

## 5. Testing JWT Authentication

To verify JWT auth is working:

1. Create a meeting in Django
2. Join the meeting - you should be authenticated automatically
3. Check Jitsi logs for JWT validation messages:

```bash
docker-compose logs -f prosody
```

You should see successful JWT validation messages rather than anonymous authentication.

## 6. Feature Control

The Django app allows enabling/disabling features. To ensure these settings work:

1. Verify the features in your Docker Jitsi setup:
   - Recording requires additional Jib Recorder configuration
   - Live streaming requires additional setup
   - End-to-end encryption should be enabled in the Docker config

2. Test each feature from the Django interface to verify it's working correctly

## 7. Production Deployment

For production:

1. Use a proper web server (nginx, Apache) to serve Django with media files
2. Set up HTTPS for both Django and Jitsi
3. Use the same domain or subdomain for best integration
4. Configure persistent storage for media files

Example nginx configuration:

```
server {
    listen 80;
    server_name your-portfolio-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name your-portfolio-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /media/ {
        alias /path/to/your/media_files/;
    }
    
    location / {
        proxy_pass http://django_app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 8. Common Issues and Solutions

### JWT Authentication Issues

If JWT authentication fails:

1. Verify that `JWT_APP_ID` and `JWT_APP_SECRET` match between Django and Docker
2. Check that the issued JWT token has the correct audience and issuer
3. Confirm that the token expiry is set correctly

### Meeting Joining Issues

If you can't join meetings:

1. Check browser console for JavaScript errors
2. Verify that your Jitsi domain is accessible from the browser
3. Confirm that WebSockets are correctly configured (needed for video/audio)

### Customization Issues

If customizations don't appear:

1. Check that the media files are being served correctly
2. Verify the URLs in the configuration match the actual file locations
3. Ensure the Jitsi iframe API is receiving the correct configuration

## 9. Next Steps

After basic integration, consider:

1. Setting up a websocket connection for real-time meeting updates
2. Implementing meeting recordings storage in your Django app
3. Adding analytics to track meeting usage
4. Integrating with other portfolio apps for a seamless experience