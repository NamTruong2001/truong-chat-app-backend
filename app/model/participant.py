from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, relationship
from db.db_config import Base
from enums import UserConversationRole

class ParticipantModel(Base):
    __tablename__ = "participants"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(UserConversationRole))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    conversation: Mapped["ConversationModel"] = relationship(back_populates="participants")
    user: Mapped["UserModel"] = relationship()

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}