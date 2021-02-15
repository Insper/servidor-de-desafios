# Source: https://github.com/druids/django-chamber/blob/master/chamber/storages/boto3.py
from django.core.files.base import ContentFile
from storages.backends.s3boto3 import S3Boto3Storage


def force_bytes_content(content, blocksize=1024):
    """Returns a tuple of content (file-like object) and bool indicating wheter the content has been casted or not"""
    block = content.read(blocksize)
    content.seek(0)

    if not isinstance(block, bytes):
        _content = bytes(
            content.read(),
            'utf-8' if not hasattr(content, 'encoding') or content.encoding is None else content.encoding,
        )
        return ContentFile(_content), True
    return content, False


class MediaStorage(S3Boto3Storage):
    bucket_name = 'softdes-static'
    location = 'media'

    def _clean_name(self, name):
        # pathlib support
        return super()._clean_name(str(name))

    def save(self, name, content, max_length=None):
        content, _ = force_bytes_content(content)
        return super().save(name, content, max_length)
