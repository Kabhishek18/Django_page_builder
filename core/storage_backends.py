from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    Custom S3 storage for media files
    """
    location = 'media'
    file_overwrite = False