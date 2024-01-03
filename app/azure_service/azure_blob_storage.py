import uuid
from datetime import datetime, timedelta

import pytz
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions, generate_container_sas, \
    ContainerSasPermissions

from config import get_settings
from validator import validate_upload_file_to_azure_blob_service
from fastapi import UploadFile, HTTPException

settings = get_settings()
class AzureBlobStorageService:
    def __init__(self, blob_service_client: BlobServiceClient):
        self.blob_service_client = blob_service_client

    def create_blob_container(self, container_name):
        try:
            container_client = self.blob_service_client.create_container(name=container_name)
        except ResourceExistsError:
            print('A container with this name already exists')

    async def upload_blob_from_upload_file(self,
                                           file: UploadFile,
                                           container_name: str = settings.azure_blob_container) -> tuple[str, str, str]:
        try:
            await validate_upload_file_to_azure_blob_service(file)
        except Exception as ie:
            raise HTTPException(detail=ie.message, status_code=400)

        uuid_str = str(uuid.uuid4())
        file_content_split = file.content_type.split("/")
        file_type = file_content_split[0]
        file_extension = file_content_split[1]
        uuid_filename = f"{uuid_str}.{file_extension}"

        file_content = await file.read()
        container_client = self.blob_service_client.get_blob_client(container_name, blob=uuid_filename)
        container_client.upload_blob(file_content, content_type=file.content_type)

        return file_type, uuid_filename, file.filename

    def get_blob_sas_read_permission_url(self,
                                         blob_name: str,
                                         account_name=settings.azure_account_name,
                                         account_key=settings.azure_storage_account_key,
                                         container_name=settings.azure_blob_container,
                                         expire_time: int = 1
                                         ) -> str:
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time_vietnam = datetime.now(tz=vietnam_timezone)
        current_time_utc = current_time_vietnam.astimezone(pytz.utc)

        # Define the start and expiration times (1 hour validity)
        start_time = current_time_utc
        expiry_time = start_time + timedelta(hours=expire_time)

        sas_blob_token = generate_blob_sas(account_name=account_name,
                                           container_name=container_name,
                                           blob_name=blob_name,
                                           account_key=account_key,
                                           permission=BlobSasPermissions(read=True),
                                           start=start_time,
                                           expiry=expiry_time)

        return f"{settings.azure_blob_acc_url}/{container_name}/{blob_name}?{sas_blob_token}"

    def get_container_sas_read_permisson_token(self,
                                         account_name=settings.azure_account_name,
                                         account_key=settings.azure_storage_account_key,
                                         container_name=settings.azure_blob_container,
                                         expire_time: int = 1) -> str:
        vietnam_timezone = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time_vietnam = datetime.now(tz=vietnam_timezone)
        current_time_utc = current_time_vietnam.astimezone(pytz.utc)

        # Define the start and expiration times (1 hour validity)
        start_time = current_time_utc
        expiry_time = start_time + timedelta(hours=expire_time)

        sas_container_token = generate_container_sas(account_name=account_name,
                                                     container_name=container_name,
                                                     account_key=account_key,
                                                     permission=ContainerSasPermissions(read=True),
                                                     start=start_time,
                                                     expiry=expiry_time)

        return f"{container_name}?{sas_container_token}"
