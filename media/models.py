from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.utils.text import slugify
import os
import uuid


class MediaFolder(models.Model):
    """
    Folders for organizing media files
    """
    name = models.CharField(_('Name'), max_length=100)
    slug = models.SlugField(_('Slug'), max_length=100)
    parent = models.ForeignKey('self', verbose_name=_('Parent Folder'), related_name='children',
                             on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Media Folder')
        verbose_name_plural = _('Media Folders')
        unique_together = ('parent', 'slug')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent}/{self.name}"
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_path(self):
        """Get the full path of the folder"""
        if self.parent:
            return f"{self.parent.get_path()}/{self.slug}"
        return self.slug
    
    def get_absolute_url(self):
        """Get the admin URL for this folder"""
        return f"/admin/media/mediafolder/{self.id}/change/"
        
    def get_media_items(self):
        """Get all media items in this folder"""
        return self.media_items.all()


def get_upload_path(instance, filename):
    """Dynamically determine upload path based on folder structure"""
    if instance.folder:
        return os.path.join('uploads', instance.folder.get_path(), filename)
    return os.path.join('uploads', filename)


class MediaItem(models.Model):
    """
    Media items (images, documents, etc.) with metadata
    """
    # Basic information
    title = models.CharField(_('Title'), max_length=255)
    file = models.FileField(_('File'), upload_to=get_upload_path)
    file_name = models.CharField(_('File Name'), max_length=255, editable=False)
    file_size = models.BigIntegerField(_('File Size'), editable=False, default=0)
    file_type = models.CharField(_('File Type'), max_length=100, editable=False)
    
    # Type categorization
    MEDIA_TYPE_CHOICES = (
        ('image', _('Image')),
        ('document', _('Document')),
        ('video', _('Video')),
        ('audio', _('Audio')),
        ('other', _('Other')),
    )
    media_type = models.CharField(_('Media Type'), max_length=20, choices=MEDIA_TYPE_CHOICES, default='other')
    
    # Organization
    folder = models.ForeignKey(MediaFolder, verbose_name=_('Folder'), related_name='media_items',
                             on_delete=models.SET_NULL, null=True, blank=True)
    
    # Image specific fields
    width = models.IntegerField(_('Width'), null=True, blank=True)
    height = models.IntegerField(_('Height'), null=True, blank=True)
    
    # Metadata
    alt_text = models.CharField(_('Alt Text'), max_length=255, blank=True,
                              help_text=_('Alternative text for accessibility'))
    description = models.TextField(_('Description'), blank=True)
    uploaded_by = models.ForeignKey(User, verbose_name=_('Uploaded By'),
                                  on_delete=models.SET_NULL, null=True, blank=True)
    uploaded_at = models.DateTimeField(_('Uploaded At'), auto_now_add=True)
    modified_at = models.DateTimeField(_('Modified At'), auto_now=True)
    
    # Additional attributes
    is_featured = models.BooleanField(_('Featured'), default=False)
    uuid = models.UUIDField(_('UUID'), default=uuid.uuid4, editable=False)
    
    class Meta:
        verbose_name = _('Media Item')
        verbose_name_plural = _('Media Items')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Extract file metadata if it's a new upload
        if self.file and not self.file_name:
            # File name
            self.file_name = os.path.basename(self.file.name)
            
            # File size
            try:
                self.file_size = self.file.size
            except (AttributeError, FileNotFoundError):
                pass
            
            # File type
            file_ext = os.path.splitext(self.file_name)[1].lower()
            self.file_type = file_ext[1:] if file_ext else ''
            
            # Determine media type based on file extension
            image_types = ['jpg', 'jpeg', 'png', 'gif', 'svg', 'webp']
            document_types = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'rtf', 'ppt', 'pptx']
            video_types = ['mp4', 'avi', 'mov', 'wmv', 'webm']
            audio_types = ['mp3', 'wav', 'ogg', 'flac']
            
            if self.file_type in image_types:
                self.media_type = 'image'
                # Get image dimensions
                try:
                    from PIL import Image
                    img = Image.open(self.file)
                    self.width, self.height = img.size
                except Exception:
                    pass
            elif self.file_type in document_types:
                self.media_type = 'document'
            elif self.file_type in video_types:
                self.media_type = 'video'
            elif self.file_type in audio_types:
                self.media_type = 'audio'
            else:
                self.media_type = 'other'
        
        # If title is not provided, use filename
        if not self.title:
            self.title = os.path.splitext(self.file_name)[0]
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Return the URL to the media item"""
        return self.file.url if self.file else ''
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def is_image(self):
        """Check if this is an image file"""
        return self.media_type == 'image'
    
    def get_thumbnail_url(self):
        """Return the thumbnail URL for images"""
        if self.is_image():
            # If using sorl-thumbnail or similar, generate thumbnail
            # For now, just return the original image URL
            return self.file.url
        
        # Return appropriate icon based on media type
        return f"/static/img/icons/{self.media_type}.png"