import sys
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    mysql_db_user: str
    mysql_db_name: str
    mysql_db_password: str
    mysql_db_host: str
    mysql_db_port: str
    mongo_user: str
    mongo_password: str
    mongo_port: str
    mongo_host: str
    azure_blob_acc_url: str
    azure_blob_container: str
    azure_account_name: str
    azure_storage_account_key: str
    jwt_secret_key: str
    jwt_algorithm: str
    redis_host: str
    redis_port: str
    redis_db: str
    redis_password: str
    redis_user: str
    allowed_images_type: list[str] = ["image/png", "image/gif", "image/jpeg", "image/jpg"]
    allowed_video_type: list[str] = ["video/mp4"]

    model_config = SettingsConfigDict(env_file=f"../.{sys.argv[1] if len(sys.argv) > 1 else 'local'}")


@lru_cache()
def get_settings():
    return Settings()
