from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from pagebuilder.models import Page


class PageSitemap(Sitemap):
    """
    Sitemap for all published pages
    """
    changefreq = 'weekly'
    priority = 0.5
    
    def items(self):
        """Return all published pages"""
        return Page.objects.filter(status='published')
    
    def lastmod(self, obj):
        """Return the last modified date"""
        return obj.updated_at
    
    def location(self, obj):
        """Return the URL of the page"""
        return obj.get_absolute_url()
    
    def priority(self, obj):
        """
        Set priority based on page importance
        Homepage gets highest priority, followed by top-level pages
        """
        if obj.is_homepage:
            return 1.0
        elif obj.parent is None:
            return 0.8
        else:
            return 0.5