from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.contrib import messages
from django.views.generic import TemplateView, DetailView, FormView
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from pagebuilder.models import Page, Block
from .forms import ContactForm, NewsletterForm
from .models import SiteSettings, ContactMessage, NewsletterSubscriber


def get_site_settings():
    """Retrieve global site settings"""
    try:
        return SiteSettings.objects.first()
    except:
        return None


class HomePageView(TemplateView):
    """
    View for rendering the home page.
    This will automatically find the page marked as homepage.
    """
    template_name = 'pages/home.html'
    
    def get(self, request, *args, **kwargs):
        try:
            # Find the page marked as homepage
            homepage = Page.objects.filter(is_homepage=True, status='published').first()
            
            if homepage:
                # Render with the page detail view
                return PageDetailView.as_view()(
                    request, 
                    slug=homepage.slug,
                    *args, 
                    **kwargs
                )
            else:
                # If no homepage is set, use the default template
                return super().get(request, *args, **kwargs)
        except Exception as e:
            # Log the error and render default template
            print(f"Error loading homepage: {e}")
            return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['site_settings'] = get_site_settings()
        return context


class PageDetailView(DetailView):
    """
    View for rendering a specific page using its slug.
    """
    model = Page
    context_object_name = 'page'
    
    def get_object(self, queryset=None):
        """Get the published page by slug"""
        if queryset is None:
            queryset = self.get_queryset()
            
        slug = self.kwargs.get('slug')
        
        if not slug:
            raise Http404(_("Page not found"))
            
        # Filter for published pages only
        queryset = queryset.filter(status='published')
            
        try:
            obj = queryset.get(slug=slug)
        except queryset.model.DoesNotExist:
            raise Http404(_("No page found matching the query"))
            
        return obj
    
    def get_template_names(self):
        """Determine which template to use based on page and active theme"""
        page = self.get_object()
        theme_dir = ''
        
        try:
            from themes.models import Theme
            active_theme = Theme.objects.filter(is_active=True).first()
            if active_theme:
                theme_dir = active_theme.directory
        except:
            pass
            
        # Try theme-specific template first
        if theme_dir:
            templates = [
                f'themes/{theme_dir}/pages/{page.slug}.html',
                f'themes/{theme_dir}/pages/default.html',
            ]
        else:
            templates = []
        
        # Fall back to default templates
        templates.extend([
            f'pages/{page.slug}.html',
            'pages/default.html',
        ])
        
        if page.is_homepage:
            if theme_dir:
                templates.insert(0, f'themes/{theme_dir}/pages/home.html')
            templates.insert(len(templates) - 1, 'pages/home.html')
        
        return templates
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.object
        
        # Add site settings
        context['site_settings'] = get_site_settings()
        
        # Add blocks to context
        context['blocks'] = page.get_blocks()
        
        # Add page settings
        context['page_settings'] = page.get_page_settings()
        
        # Add form context for contact pages
        if 'contact' in page.slug or page.get_page_settings().get('has_contact_form', False):
            context['contact_form'] = ContactForm()
            
        # Add newsletter form if enabled
        if page.get_page_settings().get('has_newsletter_form', False):
            context['newsletter_form'] = NewsletterForm()
        
        return context


class ContactFormView(FormView):
    """
    View for processing contact form submissions
    """
    form_class = ContactForm
    template_name = 'forms/contact.html'
    success_url = '/'
    
    def form_valid(self, form):
        # Save the contact message
        contact = ContactMessage(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )
        contact.save()
        
        # Add success message
        messages.success(self.request, _('Thank you for your message! We will contact you soon.'))
        
        # Get the redirect URL
        redirect_page = self.request.POST.get('redirect_page', None)
        
        if redirect_page:
            # If a specific redirect page was specified
            try:
                page = Page.objects.get(slug=redirect_page, status='published')
                self.success_url = page.get_absolute_url()
            except Page.DoesNotExist:
                pass
                
        return super().form_valid(form)


class NewsletterFormView(FormView):
    """
    View for processing newsletter form submissions
    """
    form_class = NewsletterForm
    template_name = 'forms/newsletter.html'
    success_url = '/'
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        name = form.cleaned_data.get('name', '')
        
        # Check if already subscribed
        subscriber, created = NewsletterSubscriber.objects.get_or_create(
            email=email,
            defaults={'name': name, 'is_active': True}
        )
        
        if created:
            messages.success(self.request, _('Thank you for subscribing to our newsletter!'))
        else:
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save()
                messages.success(self.request, _('Your subscription has been reactivated!'))
            else:
                messages.info(self.request, _('You are already subscribed to our newsletter.'))
        
        # Get the redirect URL
        redirect_page = self.request.POST.get('redirect_page', None)
        
        if redirect_page:
            # If a specific redirect page was specified
            try:
                page = Page.objects.get(slug=redirect_page, status='published')
                self.success_url = page.get_absolute_url()
            except Page.DoesNotExist:
                pass
                
        return super().form_valid(form)