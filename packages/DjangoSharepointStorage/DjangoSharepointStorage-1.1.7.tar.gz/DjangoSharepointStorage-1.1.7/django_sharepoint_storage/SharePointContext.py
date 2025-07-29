from office365.sharepoint.client_context import ClientContext
from django.conf import settings


class SharePointContext:

    def __init__(self):
        client_id = getattr(settings, 'SHAREPOINT_APP_CLIENT_ID', 'client_id')
        sharepoint_url = getattr(settings, 'SHAREPOINT_URL', 'sharepoint_url')
        cert_path = getattr(settings, 'SHAREPOINT_API_CERTIFICATE_PATH', 'sharepoint_api_certificate_path')
        thumbprint = getattr(settings, 'SHAREPOINT_API_CERTIFICATE_THUMBPRINT', 'sharepoint_api_certificate_thumbprint')
        tenant = getattr(settings, 'SHAREPOINT_API_TENANT_NAME', 'sharepoint_api_tenant_name')

        cert_settings = {
            'client_id': client_id,
            'thumbprint': thumbprint,
            'cert_path': cert_path
        }
        self.ctx = ClientContext(sharepoint_url).with_client_certificate(tenant, **cert_settings)