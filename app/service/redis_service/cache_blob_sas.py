from typing import Union

from redis import Redis
from azure_service import AzureBlobStorageService


class RedisSasBlobCache:
    def __init__(self, redis_client: Redis, azure_blob_service: AzureBlobStorageService):
        self.__rc = redis_client
        self.az_blob_service = azure_blob_service

    def set(self, blob_name: str, value: Union[str, int], expiration=None):
        self.__rc.set(blob_name, value, ex=expiration)

    def get(self, blob_name: str):
        if not self.__rc.exists(blob_name):
            sas_url = self.az_blob_service.get_blob_sas_read_permission_url(blob_name=blob_name)
            self.set(blob_name, value=sas_url, expiration=1 * 60 * 60)
        return self.__rc.get(blob_name)

    def delete(self, blob_name):
        self.__rc.delete(blob_name)
