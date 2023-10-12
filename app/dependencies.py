from service import (AuthService, ConversationService, UserService,
                     ParticipantService, RedisSocketIOManager, RedisSasBlobCache,
                     ConversationCache)
from db import MysqlDBAdapter, mongo_db_client
from socketio_events import ini_socketio
from service.redis_service.redis_dependencies import redis_client
from azure_service import azure_blob_storage_service

db_adapter = MysqlDBAdapter()
redis_message_cache = ConversationCache(db_adapter=db_adapter, redis_client=redis_client)
redis_blob_cache = RedisSasBlobCache(redis_client=redis_client, azure_blob_service=azure_blob_storage_service)
redis_socket_io_id_manager = RedisSocketIOManager(redis_client)
auth_service = AuthService(db_adapter)
participant_service = ParticipantService(db_adapter)
conversation_service = ConversationService(db_adapter=db_adapter,
                                           redis_sas_cache_service=redis_blob_cache,
                                           redis_message_cache=redis_message_cache,
                                           mongo_db_client=mongo_db_client)
user_service = UserService(db_adapter)
sio = ini_socketio(socketio_manager=redis_socket_io_id_manager,
                   conversation_service=conversation_service,
                   auth_service=auth_service,
                   participant_service=participant_service)
