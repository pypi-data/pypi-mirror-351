import platform
from django.core.files.storage import Storage
import os
import datetime
import time
from io import BytesIO
from django.conf import settings
from django.db import connection

from django_sharepoint_storage.SharePointContext import SharePointContext
from django_sharepoint_storage.SharePointFile import SharePointFile
import threading

DB_NAME = connection.settings_dict['NAME']

mutex = threading.Lock()

class SharePointStorage(Storage):
    sharepoint_url = getattr(settings, 'SHAREPOINT_URL', 'sharepoint_url')

    def __init__(self, location='uploads', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = location

    @staticmethod
    def print_failure(retry_number, ex):
        print(f"{retry_number}: {ex}")
        if retry_number == 15:
            raise ex

    def _open(self, name, mode='rb', retries=15):
        from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path

        if mode in ['r', 'rb']:
            file_url = self.url(name)
            ctx = SharePointContext().ctx
            file = ctx.web.get_file_by_server_relative_path(
                get_server_relative_path(file_url)).execute_query_retry(max_retry=15, timeout_secs=5,
                                                                        failure_callback=SharePointStorage.print_failure)
            if retries <= 0:
                raise Exception("SharePoint Server cannot handle requests at the moment.")
            try:
                binary_file = file.open_binary(ctx, get_server_relative_path(file_url))
                bytesio_object = BytesIO(binary_file.content)
                return bytesio_object
            except Exception as ex:
                if ex.response.status_code == 404:
                    raise ex
                time.sleep(5)
                return self._open(name, mode, retries - 1)

        elif mode in ['w', 'wb', "w+", "wb+"]:
            return SharePointFile(name, mode, self)
        else:
            raise ValueError(f"Unsupported file mode: {mode}")

    def _save(self, name, content):
        with mutex:
            ctx = SharePointContext().ctx
            folder_path = f"Shared Documents/{os.getenv('DEPLOYMENT_ENVIRONMENT', 'LOCAL')}-{os.getenv('K8S_NAMESPACE', 'ENV')}/{os.getenv('KEYCLOAK_INTERNAL_CLIENT_ID', 'Local')}/{os.getenv('INSTANCE_RESOURCE_IDENTIFIER', f'{platform.node()}/{DB_NAME}')}/{self.location}/{os.path.dirname(name)}"
            target_folder = ctx.web.ensure_folder_path(folder_path).execute_query_retry(max_retry=15, timeout_secs=5,
                                                            failure_callback=SharePointStorage.print_failure)
            content.seek(0)
            file_content = content.read()

            target_folder.upload_file(os.path.basename(name), file_content).execute_query_retry(max_retry=15, timeout_secs=5,
                                                                                                failure_callback=SharePointStorage.print_failure)

            return name

    def delete(self, name):
        from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path
        with mutex:
            ctx = SharePointContext().ctx

            file_path = get_server_relative_path(self.url(name))
            file = ctx.web.get_file_by_server_relative_path(file_path).get().execute_query_retry(max_retry=15,
                                                                                                          timeout_secs=5,
                                                                                                          failure_callback=SharePointStorage.print_failure)
            file.delete_object().execute_query_retry(max_retry=15, timeout_secs=5,
                                                     failure_callback=SharePointStorage.print_failure)

    def exists(self, name, retries=15):
        from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path
        with mutex:
            file_path = get_server_relative_path(self.url(name))

            ctx = SharePointContext().ctx

            if retries <= 0:
                raise Exception("SharePoint Server cannot handle requests at the moment.")
            try:
                if name.endswith('/'):
                    ctx.web.get_folder_by_server_relative_path(file_path).get().execute_query()
                else:
                    ctx.web.get_file_by_server_relative_path(file_path).get().execute_query()
            except Exception as ex:
                if ex.response.status_code == 404:
                    return False
                time.sleep(5)
                return self.exists(name, retries - 1)

            return True

    def get_modified_time(self, name):
        from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path

        file_path = get_server_relative_path(self.url(name))

        ctx = SharePointContext().ctx

        if name.endswith('/'):
            file = ctx.web.get_folder_by_server_relative_path(file_path).get().expand(
                ["TimeLastModified"]).get().execute_query_retry(max_retry=15, timeout_secs=5,
                                                                failure_callback=SharePointStorage.print_failure)
        else:
            file = ctx.web.get_file_by_server_relative_path(file_path).get().expand(
                ["TimeLastModified"]).get().execute_query_retry(max_retry=15, timeout_secs=5,
                                                                failure_callback=SharePointStorage.print_failure)

        return datetime.datetime.timestamp(file.time_last_modified)

    def listdir(self, name):
        from django_sharepoint_storage.SharePointCloudStorageUtils import get_server_relative_path

        ctx = SharePointContext().ctx

        folder_path = get_server_relative_path(self.url(name))

        root_folder = ctx.web.get_folder_by_server_relative_path(folder_path).get().execute_query_retry(
            max_retry=15, timeout_secs=5, failure_callback=SharePointStorage.print_failure)
        files = root_folder.get_files(recursive=False).execute_query_retry(max_retry=15, timeout_secs=5,
                                                                           failure_callback=SharePointStorage.print_failure)
        return [f.name for f in root_folder.folders], [f.name for f in files]

    def url(self, name):
        # Use the dirname of name as your upload_to equivalent
        return f"{self.sharepoint_url}/Shared Documents/{os.getenv('DEPLOYMENT_ENVIRONMENT', 'LOCAL')}-{os.getenv('K8S_NAMESPACE', 'ENV')}/{os.getenv('KEYCLOAK_INTERNAL_CLIENT_ID', 'Local')}/{os.getenv('INSTANCE_RESOURCE_IDENTIFIER', f'{platform.node()}/{DB_NAME}')}/{self.location}/{name}"
