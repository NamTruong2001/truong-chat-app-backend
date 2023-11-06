import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")

MYSQL_DB_USER = os.environ["MYSQL_DB_USER"]
MYSQL_DB_NAME = os.environ["MYSQL_DB_NAME"]
MYSQL_DB_PASSWORD = os.environ["MYSQL_DB_PASSWORD"]
MYSQL_DB_HOST = os.environ["MYSQL_DB_HOST"]
MYSQL_DB_PORT = os.environ["MYSQL_DB_PORT"]
MONGO_USER = os.environ["MONGO_USER"]
MONGO_PASSWORD = os.environ["MONGO_PASSWORD"]
MONGO_PORT = os.environ["MONGO_PORT"]
MONGO_HOST = os.environ["MONGO_HOST"]
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