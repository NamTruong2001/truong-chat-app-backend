from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, Integer, Enum
from sqlalchemy.orm import Mapped, relationship
from db.database import Base
from enums import ConversationRole

class ParticipantModel(Base):
    id = Column(Integer)
    conversation_id = Column(Integer, ForeignKey("conversation.id"))
    users_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(ConversationRole))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    conversation: Mapped["ConversationModel"] = relationship(back_populates="participants")