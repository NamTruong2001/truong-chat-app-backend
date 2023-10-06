from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from global_variables import AZURE_BLOB_STORAGE_URL
from .azure_blob_storage import AzureBlobStorageService

token_credential = DefaultAzureCredential(exclude_interactive_browser_credential=False)

blob_service_client = BlobServiceClient(
        account_url=AZURE_BLOB_STORAGE_URL,
        credential=token_credential)

azure_blob_storage_service = AzureBlobStorageService(blob_service_client=blob_service_client)

