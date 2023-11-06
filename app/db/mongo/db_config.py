from pymongo import MongoClient
from global_variables import MONGO_USER, MONGO_PASSWORD, MONGO_PORT, MONGO_HOST

mongo_uri = f"mongodb://{MONGO_USER}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}"
mongo_db_client = MongoClient(mongo_uri)
# mongo_db_client.get_database("truong_chat_app")
