# jitsi/storage.py

from django.conf import settings
from django.core.files.storage import FileSystemStorage

class JitsiMediaStorage(FileSystemStorage):
    """
    Custom storage for Jitsi media files to use local filesystem instead of S3
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)