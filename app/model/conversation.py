from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, relationship
from db.database import Base
from typing import List


class ConversationModel(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = Column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = Column(String(length=50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey("users.id"))

    creator: Mapped["UserModel"] = relationship()
    messages: Mapped[List["MessageModel"]] = relationship(back_populates="conversation")
    participants: Mapped[List["ParticipantModel"]] = relationship(back_populates="conversation")
