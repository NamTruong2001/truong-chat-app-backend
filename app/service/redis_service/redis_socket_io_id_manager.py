from redis import Redis

class RedisSocketIOManager:
    def __init__(self, r: Redis):
        self.__rc = r
        self.__user_sockets_template = "user:{}:socketids"

    def add_online_user_id(self, user_id) -> int:
        return self.__rc.sadd("online_user_ids", user_id)

    def remove_socket_id_from_user(self, sid, user_id) -> int:
        set_key = self.__user_sockets_template.format(user_id)
        i = self.__rc.srem(set_key, sid)
        if self.__rc.scard(set_key) == 0:
            self.__rc.expire(set_key, 10)
            self.remove_user_connection(user_id)
        return i

    def add_user_socketio_id_connection(self, user_id, sid) -> int:
        if self.is_user_online(user_id) is False:
            self.add_online_user_id(user_id)
        set_key = self.__user_sockets_template.format(user_id)
        return self.__rc.sadd(set_key, sid)

    def get_number_of_user_connection(self, user_id) -> int:
        set_key = self.__user_sockets_template.format(user_id)
        return self.__rc.scard(set_key)

    def get_user_socketio_ids(self, user_id) -> set:
        set_key = self.__user_sockets_template.format(user_id)
        return self.__rc.smembers(set_key)

    def remove_user_connection(self, user_id) -> int:
        return self.__rc.srem("online_user_ids", user_id)

    def is_user_online(self, user_id) -> bool:
        return bool(self.__rc.sismember("online_user_ids", user_id))

    def find_online_users_by_ids(self, user_ids: list[int]) -> list:
        self.__rc.sadd("temp_user_ids", *user_ids)
        intersect_values =  self.__rc.sinter(["online_user_ids","temp_user_ids"])
        self.__rc.delete("temp_user_ids")
        return intersect_values


