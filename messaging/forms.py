# messaging/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from .models import Conversation, Message, Participant


class MessageForm(forms.ModelForm):
    """Form for creating and sending messages"""
    
    attachment = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*,video/*,audio/*,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain',
        })
    )
    
    class Meta:
        model = Message
        fields = ['content', 'attachment']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 1,
                'placeholder': _('Type your message here...'),
                'required': True,
                'autofocus': True,
            }),
        }

    def clean_attachment(self):
        """Validate attachment size"""
        attachment = self.cleaned_data.get('attachment')
        if attachment:
            # Limit to 10MB
            if attachment.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_("File is too large. Maximum size is 10MB."))
        return attachment


class PrivateConversationForm(forms.Form):
    """Form for creating a new private conversation with a user"""
    
    recipient = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label=_('Send message to'),
        widget=forms.Select(attrs={
            'class': 'form-control form-select',
            'data-placeholder': _('Search for a user...'),
        })
    )
    
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Type your message here...'),
        })
    )
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Exclude current user from recipients
        if current_user:
            self.fields['recipient'].queryset = User.objects.exclude(id=current_user.id).filter(is_active=True)


class GroupConversationForm(forms.ModelForm):
    """Form for creating a new group conversation"""
    
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label=_('Participants'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control form-select',
            'data-placeholder': _('Select participants...'),
        })
    )
    
    initial_message = forms.CharField(
        label=_('Initial Message'),
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': _('Send an optional initial message to the group...'),
        })
    )
    
    class Meta:
        model = Conversation
        fields = ['name', 'description', 'image', 'participants', 'initial_message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Group name'),
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': _('Group description (optional)'),
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Exclude current user from participants selection
        if current_user:
            self.fields['participants'].queryset = User.objects.exclude(id=current_user.id).filter(is_active=True)
            
    def clean_image(self):
        """Validate image size and format"""
        image = self.cleaned_data.get('image')
        if image:
            # Limit to 5MB
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError(_("Image is too large. Maximum size is 5MB."))
            
            # Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = image.name.lower().split('.')[-1]
            if '.' + file_extension not in allowed_extensions:
                raise forms.ValidationError(_("Only JPG, JPEG, PNG, and GIF images are allowed."))
        return image
            
    def save(self, commit=True, creator=None):
        # Set conversation type to 'group'
        instance = super().save(commit=False)
        instance.type = 'group'
        instance.creator = creator
        
        if commit:
            instance.save()
            
            # Add selected participants to the conversation
            participants = self.cleaned_data.get('participants', [])
            for user in participants:
                instance.add_participant(user)
                
            # Add creator as an admin participant
            if creator:
                instance.add_participant(creator, is_admin=True)
                
            # Create initial message if provided
            initial_message = self.cleaned_data.get('initial_message')
            if initial_message and creator:
                Message.objects.create(
                    conversation=instance,
                    sender=creator,
                    content=initial_message
                )
                
        return instance


class BroadcastForm(forms.ModelForm):
    """Form for creating a broadcast message"""
    
    recipients = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label=_('Recipients'),
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control form-select',
            'data-placeholder': _('Select recipients...'),
        })
    )
    
    message = forms.CharField(
        label=_('Broadcast Message'),
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': _('Enter your broadcast message here...'),
        })
    )
    
    class Meta:
        model = Conversation
        fields = ['name', 'recipients', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Broadcast title (optional)'),
            }),
        }
    
    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Exclude current user from recipients
        if current_user:
            self.fields['recipients'].queryset = User.objects.exclude(id=current_user.id).filter(is_active=True)
    
    def save(self, commit=True, sender=None):
        # Set conversation type to 'broadcast'
        instance = super().save(commit=False)
        instance.type = 'broadcast'
        instance.creator = sender
        
        if commit:
            instance.save()
            
            # Add recipients to the conversation
            recipients = self.cleaned_data.get('recipients', [])
            for user in recipients:
                instance.add_participant(user)
                
            # Add sender as an admin participant
            if sender:
                instance.add_participant(sender, is_admin=True)
                
            # Create the broadcast message
            message_content = self.cleaned_data.get('message')
            if message_content and sender:
                Message.objects.create(
                    conversation=instance,
                    sender=sender,
                    content=message_content
                )
                
        return instance