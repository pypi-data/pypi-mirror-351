from pathlib import Path
from urllib.parse import urlparse
from django.conf import settings
from django_sharepoint_storage.SharePointStorage import SharePointStorage

Static = lambda: SharePointStorage(location=getattr(settings, 'SHAREPOINT_STATIC_DIR', 'sharepoint_static_dir'))
Media = lambda: SharePointStorage(location=getattr(settings, 'SHAREPOINT_MEDIA_DIR', 'sharepoint_media_dir'))

def get_server_relative_path(url):
    parse_result = urlparse(url)
    path_parts = Path(parse_result.path).parts
    if path_parts:
        return '/'.join(path_parts)[1:]
    else:
        return ''