import socketio

from config import get_settings
from db.mysql.db_config import SessionLocal
from service import (
    AuthService,
    ConversationService,
    UserService,
    ParticipantService,
    RedisSocketIOManager,
    RedisSasBlobCache,
    ConversationCache,
)
from db import MysqlDBAdapter, OneConnectionOnlyMysqlDBAdapter
from service.redis_service.redis_dependencies import redis_client
from azure_service import azure_blob_storage_service
from socketio_events.chat_server import ChatServer

# db_adapter = MysqlDBAdapter()
db_adapter = OneConnectionOnlyMysqlDBAdapter(SessionLocal())
redis_message_cache = ConversationCache(
    db_adapter=db_adapter, redis_client=redis_client
)
redis_blob_cache = RedisSasBlobCache(
    redis_client=redis_client, azure_blob_service=azure_blob_storage_service
)
redis_socket_io_id_manager = RedisSocketIOManager(redis_client)
auth_service = AuthService(db_adapter)
participant_service = ParticipantService(db_adapter)
conversation_service = ConversationService(
    db_adapter=db_adapter,
    redis_sas_cache_service=redis_blob_cache,
    redis_message_cache=redis_message_cache,
)
user_service = UserService(db_adapter)
settings = get_settings()
chat_server = ChatServer(
    socketio_manager=redis_socket_io_id_manager,
    conversation_service=conversation_service,
    auth_service=auth_service,
    participant_service=participant_service,
    name_space="/chat",
)
mgr = socketio.AsyncRedisManager(
    f"redis://{settings.redis_user}:{settings.redis_password}@{settings.redis_host}:{settings.redis_port}"
)
sio = socketio.AsyncServer(
    client_manager=mgr, cors_allowed_origins="*", async_mode="asgi"
)
sio.register_namespace(chat_server)
