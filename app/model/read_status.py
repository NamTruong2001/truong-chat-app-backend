from sqlalchemy import Integer, Column, ForeignKey, DateTime

from db import Base


class ReadStatusModel(Base):
    __tablename__ = "read_status"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    last_seen_message_id = Column(Integer, ForeignKey("messages.id"))
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    read_at = Column(DateTime)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

