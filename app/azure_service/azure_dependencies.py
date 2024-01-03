from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

from config import get_settings
from .azure_blob_storage import AzureBlobStorageService

settings = get_settings()

token_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

blob_service_client = BlobServiceClient(
        account_url=settings.azure_blob_acc_url,
        credential=token_credential)

azure_blob_storage_service = AzureBlobStorageService(blob_service_client=blob_service_client)

