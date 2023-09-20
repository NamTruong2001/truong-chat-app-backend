from sqlalchemy import Column, String, BigInteger, ForeignKey, DateTime, Integer, desc, Enum
from sqlalchemy.orm import Mapped, relationship
from db.database import Base
from typing import List
from enums import ConversationTypeEnum


class ConversationModel(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = Column(BigInteger, primary_key=True, index=True)
    title: Mapped[str] = Column(String(length=50))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    creator_id = Column(Integer, ForeignKey("users.id"))
    type = Column(Enum(ConversationTypeEnum))

    creator: Mapped["UserModel"] = relationship()
    messages: Mapped[list["MessageModel"]] = relationship(back_populates="conversation",
                                                          order_by="desc(MessageModel.created_at)")
    participants: Mapped[List["ParticipantModel"]] = relationship(back_populates="conversation")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
