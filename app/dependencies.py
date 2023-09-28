from service import SocketioIDManager, AuthService, ConversationService, UserService
from db import DBAdapter
from socketio_events import ini_socketio

socketio_id_manager = SocketioIDManager()
db_adapter = DBAdapter()
auth_service = AuthService(db_adapter)
conversation_service = ConversationService(db_adapter)
user_service = UserService(db_adapter)
sio = ini_socketio(db_adapter=db_adapter,
                   socketio_manager=socketio_id_manager,
                   conversation_service=conversation_service,
                   auth_service=auth_service)