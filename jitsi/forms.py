# jitsi/forms.py
from django import forms
from django.utils.text import slugify
from .models import JitsiRoom, JitsiCustomization, JitsiFeatureConfig


class JitsiRoomForm(forms.ModelForm):
    """
    Form for creating and updating Jitsi rooms
    """
    class Meta:
        model = JitsiRoom
        fields = ['name', 'description', 'scheduled_at', 'is_public', 'password_protected', 'moderator_password', 'attendee_password']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make password fields required if password protection is enabled
        self.fields['moderator_password'].required = False
        self.fields['attendee_password'].required = False
        
        # Add help texts
        self.fields['is_public'].help_text = "If enabled, anyone with the link can join the meeting."
        self.fields['password_protected'].help_text = "If enabled, participants will need to enter a password to join."
    
    def clean(self):
        cleaned_data = super().clean()
        password_protected = cleaned_data.get('password_protected')
        moderator_password = cleaned_data.get('moderator_password')
        attendee_password = cleaned_data.get('attendee_password')
        
        if password_protected:
            if not moderator_password:
                self.add_error('moderator_password', 'Moderator password is required when password protection is enabled.')
            if not attendee_password:
                self.add_error('attendee_password', 'Attendee password is required when password protection is enabled.')
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Generate slug from name if not present
        if not instance.slug:
            instance.slug = slugify(instance.name)
        
        if commit:
            instance.save()
        
        return instance


class JitsiCustomizationForm(forms.ModelForm):
    """
    Form for customizing Jitsi UI
    """
    class Meta:
        model = JitsiCustomization
        fields = [
            'name', 'logo', 'favicon', 'background_image', 'watermark_image',
            'primary_color', 'secondary_color', 'background_color',
            'show_footer', 'footer_text', 'custom_css', 'custom_js'
        ]
        widgets = {
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
            'background_color': forms.TextInput(attrs={'type': 'color'}),
            'custom_css': forms.Textarea(attrs={'rows': 5, 'class': 'code-editor', 'data-language': 'css'}),
            'custom_js': forms.Textarea(attrs={'rows': 5, 'class': 'code-editor', 'data-language': 'javascript'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.fields['logo'].help_text = "Recommended size: 100x50px. Will be displayed in the top left corner."
        self.fields['background_image'].help_text = "Image that will be displayed as the background."
        self.fields['watermark_image'].help_text = "Small logo that will be displayed in the bottom right corner."
        self.fields['custom_css'].help_text = "Custom CSS to be applied to the Jitsi interface."
        self.fields['custom_js'].help_text = "Custom JavaScript that will be executed when the meeting loads."
        
        # Make fields optional
        for field in self.fields:
            if field not in ['name']:
                self.fields[field].required = False


class JitsiFeatureConfigForm(forms.ModelForm):
    """
    Form for configuring Jitsi features
    """
    class Meta:
        model = JitsiFeatureConfig
        fields = [
            'name', 'enable_audio', 'enable_video', 'enable_chat',
            'enable_screen_sharing', 'enable_recording', 'enable_livestreaming',
            'enable_breakout_rooms', 'enable_lobby', 'enable_end_to_end_encryption',
            'enable_password_protection', 'enable_reactions', 'enable_raise_hand',
            'enable_tile_view', 'enable_filmstrip', 'enable_polls',
            'enable_whiteboard', 'enable_blur_background'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help texts
        self.fields['enable_audio'].help_text = "Allow participants to use microphone"
        self.fields['enable_video'].help_text = "Allow participants to use camera"
        self.fields['enable_recording'].help_text = "Allow recording the meeting (requires additional server configuration)"
        self.fields['enable_livestreaming'].help_text = "Allow streaming to YouTube or other platforms"
        self.fields['enable_end_to_end_encryption'].help_text = "Enable end-to-end encryption (may disable some features)"
        
        # Group fields
        self.fieldsets = {
            'Core Features': [
                'enable_audio', 'enable_video', 'enable_chat',
                'enable_screen_sharing'
            ],
            'Advanced Features': [
                'enable_recording', 'enable_livestreaming',
                'enable_breakout_rooms', 'enable_polls',
                'enable_whiteboard'
            ],
            'Security': [
                'enable_lobby', 'enable_end_to_end_encryption',
                'enable_password_protection'
            ],
            'UI Features': [
                'enable_reactions', 'enable_raise_hand',
                'enable_tile_view', 'enable_filmstrip',
                'enable_blur_background'
            ]
        }


class JitsiInviteForm(forms.Form):
    """
    Form for inviting participants to a meeting
    """
    emails = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text="Enter email addresses, separated by commas or new lines."
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text="Optional message to include in the invitation."
    )
    
    def clean_emails(self):
        emails = self.cleaned_data.get('emails', '')
        
        # Split by commas or new lines
        email_list = [e.strip() for e in emails.replace('\n', ',').split(',') if e.strip()]
        
        # Validate each email
        invalid_emails = []
        for email in email_list:
            if not forms.EmailField().clean(email):
                invalid_emails.append(email)
        
        if invalid_emails:
            raise forms.ValidationError(
                f"The following emails are invalid: {', '.join(invalid_emails)}"
            )
        
        return email_list