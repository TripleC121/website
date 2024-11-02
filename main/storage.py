from django.conf import settings
from django.contrib.staticfiles.storage import StaticFilesStorage
from storages.backends.s3boto3 import S3Boto3Storage


class S3ImageStorage(S3Boto3Storage):
    """Storage for S3-hosted images"""

    location = "static/images"
    file_overwrite = False

    def __init__(self, *args, **kwargs):
        kwargs["bucket_name"] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs["custom_domain"] = settings.AWS_S3_CUSTOM_DOMAIN
        super().__init__(*args, **kwargs)
