import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

DB_USER = os.environ["DB_USER"]
DB_NAME = os.environ["DB_NAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = os.environ["DB_PORT"]
AZURE_BLOB_STORAGE_URL=os.environ["AZURE_BLOB_ACC_URL"]
azure_container_name = os.environ["AZURE_BLOB_CONTAINER"]
azure_storage_account_name = os.environ["AZURE_ACCOUNT_NAME"]
azure_storage_account_key = os.environ["AZURE_STORAGE_ACCOUNT_KEY"]
JWT_SECRET = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = os.environ["REDIS_PORT"]
REDIS_DB = os.environ["REDIS_DB"]
REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]