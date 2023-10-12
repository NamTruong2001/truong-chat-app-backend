from datetime import datetime

from sqlalchemy import Column, BigInteger, ForeignKey, DateTime, Integer, Enum, Text
from sqlalchemy.orm import Mapped, relationship
from db import Base
from enums import MessageEnum


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = Column(BigInteger, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    message_type = Column(Enum(MessageEnum))
    message = Column(Text)
    created_at: Mapped[datetime] = Column(DateTime)

    conversation: Mapped["ConversationModel"] = relationship(back_populates="messages")
    attachment: Mapped["AttachmentModel"] = relationship(back_populates="message", lazy='subquery')

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

