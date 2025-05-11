from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from portfolio.sitemaps import PageSitemap

sitemaps = {
    'pages': PageSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
    # Include app URLs
    path('media-manager/', include('media.urls')),
    path('themes/', include('themes.urls')),
    path('admin/pagebuilder/', include('pagebuilder.urls', namespace='pagebuilder')),
    path('meetings/', include('jitsi.urls')),
    path('messaging/', include('messaging.urls')),
    
    # Main portfolio app - should be last as it handles dynamic pages
    path('', include('portfolio.urls')),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)