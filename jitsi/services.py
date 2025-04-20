# jitsi/services.py
import json
import time
import jwt
from datetime import datetime, timedelta
from django.conf import settings
from .models import JitsiMeeting, JitsiCustomization, JitsiFeatureConfig

def generate_jwt_token(domain, app_id, app_secret, room_name, user_id, user_name, email, is_moderator=False, expiry=24):
    """
    Generate a JWT token for Jitsi authentication
    
    Args:
        domain: Jitsi domain (e.g., meet.jitsi.si)
        app_id: Application ID for JWT
        app_secret: Application secret for JWT
        room_name: Name of the meeting room
        user_id: User identifier
        user_name: Display name of the user
        email: Email of the user
        is_moderator: Whether the user is a moderator
        expiry: Token expiry time in hours
        
    Returns:
        str: JWT token
    """
    now = int(time.time())
    expiry_time = now + (expiry * 3600)  # Convert hours to seconds
    
    payload = {
        'iss': app_id,
        'aud': 'jitsi',  # Make sure this matches the JWT_ACCEPTED_AUDIENCES in Jitsi config
        'sub': domain,   # Make sure this matches with your Jitsi domain
        'exp': expiry_time,
        'nbf': now,
        'iat': now,
        'room': room_name,  # Using room ID consistently
        'context': {
            'user': {
                'id': user_id,
                'name': user_name,
                'email': email,
                'moderator': is_moderator
            }
        }
    }
    
    token = jwt.encode(payload, app_secret, algorithm='HS256')
    
    # In some JWT libraries, encode returns a byte string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    return token


def get_default_jitsi_config():
    """
    Get the default configuration for Jitsi Meet
    
    Returns:
        dict: Default configuration for Jitsi Meet
    """
    return {
        # Core settings
        'disableDeepLinking': True,
        'disableInviteFunctions': True,
        'enableClosePage': True,
        'prejoinPageEnabled': True,
        
        # UI settings
        'defaultLanguage': 'en',
        'disableThirdPartyRequests': True,
        'hideConferenceSubject': False,
        'hideConferenceTimer': False,
        'noticeMessage': '',
        
        # Behavior settings
        'enableNoAudioDetection': True,
        'enableNoisyMicDetection': True,
        'startAudioOnly': False,
        'startWithAudioMuted': False,
        'startWithVideoMuted': False,
        'startScreenSharing': False,
        
        # Feature settings
        'enableWelcomePage': False,
        'enableClosePage': True,
        'disableAudioLevels': False,
        'disableChat': False,
        'disableDocument': True,
        'disableFilmstrip': False,
        'disableInviteFunctions': True,
        'disableJoinLeaveSounds': False,
        'disablePolls': True,
        'disableReactions': False,
        'disableRemoteMute': False,
        'disableRemoteVideoMenu': False,
        'disableSelfView': False,
        'disableSelfViewSettings': False,
        'disableShortcuts': False,
        'disableTileView': False,
        'disableProfile': False,
        'disableInitialGUM': False,
        
        # Security settings
        'securityUi': {
            'hideLobbyButton': False,
            'disableLobbyPassword': False,
        },
        'lobby': {
            'enableForceMute': True,
        },
        
        # Video settings
        'constraints': {
            'video': {
                'height': {
                    'ideal': 720,
                    'max': 1080,
                    'min': 180
                }
            }
        },
        
        # Toolbar settings
        'toolbarButtons': [
            'microphone', 'camera', 'desktop', 'chat', 
            'raisehand', 'participants-pane', 'tileview',
            'select-background', 'settings', 'hangup'
        ],
        
        # Connection settings
        'websocket': 'wss://' + settings.JITSI_DOMAIN + '/xmpp-websocket',
        'bosh': 'https://' + settings.JITSI_DOMAIN + '/http-bind',
        
        # Recording settings
        'fileRecordingsEnabled': False,
        'dropbox': {
            'appKey': None,
            'redirectUri': None
        },
        
        # Live streaming settings
        'liveStreamingEnabled': False,
        'youtubeApiKey': None,
    }


def get_jitsi_config(meeting):
    """
    Get the Jitsi configuration based on the meeting settings
    
    Args:
        meeting: JitsiMeeting instance
        
    Returns:
        dict: Configuration for Jitsi Meet
    """
    # Start with default config
    config = get_default_jitsi_config()
    
    # Apply feature configuration if exists
    if meeting and meeting.feature_config:
        feature_config = meeting.feature_config.get_config_dict()
        config.update(feature_config)
        
        # Update toolbar buttons based on enabled features
        toolbar_buttons = ['microphone', 'camera', 'hangup']
        
        if feature_config.get('desktopSharingEnabled', True):
            toolbar_buttons.append('desktop')
        
        if not feature_config.get('disableChat', False):
            toolbar_buttons.append('chat')
            
        if feature_config.get('raiseHandEnabled', True):
            toolbar_buttons.append('raisehand')
            
        toolbar_buttons.append('participants-pane')
        
        if feature_config.get('tileViewEnabled', True):
            toolbar_buttons.append('tileview')
            
        if feature_config.get('virtualBackgroundEnabled', True):
            toolbar_buttons.append('select-background')
            
        toolbar_buttons.append('settings')
        
        config['toolbarButtons'] = toolbar_buttons
        
        # Update recording and streaming settings
        config['fileRecordingsEnabled'] = feature_config.get('fileRecordingsEnabled', False)
        config['liveStreamingEnabled'] = feature_config.get('liveStreamingEnabled', False)
    
    return config



def apply_customization(config, customization):
    """
    Apply UI customization to Jitsi config
    
    Args:
        config: Existing Jitsi configuration dict
        customization: JitsiCustomization instance
        
    Returns:
        dict: Updated configuration with UI customizations
    """
    if not customization:
        return config
    
    # Initialize interface config if not exists
    if 'interfaceConfig' not in config:
        config['interfaceConfig'] = {}
    
    interface_config = config['interfaceConfig']
    
    # Apply branding
    if customization.logo and hasattr(customization.logo, 'url'):
        interface_config['APP_NAME'] = customization.name
        interface_config['SHOW_BRAND_WATERMARK'] = True
        interface_config['BRAND_WATERMARK_LINK'] = customization.logo.url
    
    if customization.watermark_image and hasattr(customization.watermark_image, 'url'):
        interface_config['SHOW_WATERMARK'] = True
        interface_config['WATERMARK_LINK'] = customization.watermark_image.url
    
    # Apply colors
    interface_config['DEFAULT_BACKGROUND'] = customization.background_color
    
    # Apply footer
    interface_config['SHOW_JITSI_WATERMARK'] = customization.show_footer
    if customization.footer_text:
        interface_config['FOOTER_TEXT'] = customization.footer_text
        
    # Apply custom CSS if provided
    if customization.custom_css:
        if 'cssOverrides' not in config:
            config['cssOverrides'] = {}
        config['cssOverrides']['custom'] = customization.custom_css
        
    # Apply background image if provided
    if customization.background_image and hasattr(customization.background_image, 'url'):
        if 'dynamicBrandingUrl' not in config:
            config['dynamicBrandingUrl'] = customization.background_image.url
            
    return config

def generate_iframe_api_config(meeting, user_name, is_moderator=False):
    """
    Generate configuration for the Jitsi iframe API
    
    Args:
        meeting: JitsiMeeting instance
        user_name: Display name of the user
        is_moderator: Whether the user is a moderator
        
    Returns:
        dict: Configuration for Jitsi iframe API
    """
    room = meeting.room
    domain = settings.JITSI_DOMAIN
    
    # Get base config
    config = get_jitsi_config(meeting)
    
    # Apply UI customization
    if meeting.customization:
        config = apply_customization(config, meeting.customization)
    
    # Generate iframe options
    options = {
        'roomName': str(room.id),
        'width': '100%',
        'height': '100%',
        'parentNode': 'jitsi-container',
        'configOverwrite': config,
        'userInfo': {
            'displayName': user_name,
        },
        'interfaceConfigOverwrite': config.get('interfaceConfig', {}),
    }
    
    return options

def get_absolute_logo_url(request, logo_url):
    """
    Converts a relative logo URL to an absolute URL that can be accessed by Jitsi.
    
    Args:
        request: The HTTP request object
        logo_url: The relative URL of the logo
        
    Returns:
        str: The absolute URL of the logo
    """
    if not logo_url:
        return None
        
    # If it's already an absolute URL (starts with http), return as is
    if logo_url.startswith(('http://', 'https://')):
        return logo_url
        
    # Otherwise, construct absolute URL from the request
    return '{0}://{1}{2}'.format(
        request.scheme,
        request.get_host(),
        logo_url
    )

def prepare_logo_config(request, meeting, default_logo=None):
    """
    Prepares logo configuration for Jitsi meeting.
    
    Args:
        request: The HTTP request object
        meeting: The JitsiMeeting instance
        default_logo: Optional default logo URL to use if no customization is found
        
    Returns:
        dict: Logo configuration dictionary for Jitsi
    """
    logo_url = None
    
    # Try to get logo from meeting customization
    if meeting and meeting.customization and meeting.customization.logo:
        try:
            logo_url = meeting.customization.logo.url
        except:
            print("Error accessing logo URL from customization")
    
    # Use default logo if no logo found
    if not logo_url:
        logo_url = default_logo
        
    # Convert to absolute URL if we have a logo
    if logo_url:
        absolute_url = get_absolute_logo_url(request, logo_url)
        
        # Return configuration
        return {
            "brandingDataUrl": absolute_url,
            "watermark": {
                "display": True,
                "showJitsiWatermark": False,
                "showCustomWatermark": True,
                "customWatermarkLink": "",
                "customWatermarkPath": absolute_url
            },
            "defaultLogoUrl": absolute_url,
            "logoImageUrl": absolute_url,
            "interfaceConfig": {
                "DEFAULT_LOGO_URL": absolute_url,
                "SHOW_BRAND_WATERMARK": True,
                "BRAND_WATERMARK_URL": absolute_url
            }
        }
    
    # Return empty config if no logo is available
    return {
        "watermark": {
            "display": False,
            "showJitsiWatermark": False,
            "showCustomWatermark": False
        },
        "interfaceConfig": {
            "SHOW_BRAND_WATERMARK": False,
            "SHOW_JITSI_WATERMARK": False
        }
    }