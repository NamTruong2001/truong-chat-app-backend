class SocketioIDManager:

    def __init__(self) -> None:
        self.user_active_connections: dict[int, dict[str, None]] = {}

    def add_user_connection(self, user_id: int, sid: str):
        if user_id not in self.user_active_connections:
            self.user_active_connections[user_id] = {}
        self.user_active_connections[user_id][sid] = None

    def del_user_connection(self, user_id: int, sid: str):
        del self.user_active_connections[user_id][sid]
        if len(self.user_active_connections[user_id]) == 0:
            del self.user_active_connections[user_id]

    def get_user_sids(self, user_id):
        try:
            return self.user_active_connections[user_id].keys()
        except KeyError:
            pass

