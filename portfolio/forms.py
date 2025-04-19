from django import forms
from django.utils.translation import gettext_lazy as _


class ContactForm(forms.Form):
    """
    Contact form for website visitors
    """
    name = forms.CharField(
        label=_('Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Your Name')})
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Your Email')})
    )
    subject = forms.CharField(
        label=_('Subject'),
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Subject')})
    )
    message = forms.CharField(
        label=_('Message'),
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Your Message')})
    )
    
    # Hidden field for redirecting after submission
    redirect_page = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )


class NewsletterForm(forms.Form):
    """
    Newsletter subscription form
    """
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Your Email')})
    )
    name = forms.CharField(
        label=_('Name'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Your Name (optional)')})
    )
    
    # Hidden field for redirecting after submission
    redirect_page = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )