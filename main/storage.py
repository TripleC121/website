from django.conf import settings
from django.contrib.staticfiles.storage import StaticFilesStorage
from storages.backends.s3boto3 import S3Boto3Storage


class LocalStaticStorage(StaticFilesStorage):
    """Storage for local static files"""

    pass


class S3ImageStorage(S3Boto3Storage):
    """Storage for S3-hosted images"""

    location = "static/images"
    file_overwrite = False
