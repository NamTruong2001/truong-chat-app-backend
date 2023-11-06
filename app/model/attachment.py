from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from db import Base


class AttachmentModel(Base):
    __tablename__ = "attachment"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    file_name: Mapped[str] = Column(String(length=100))
    original_file_name: Mapped[str] = Column(String(length=50))
    message_id: Mapped[int] = Column(Integer, ForeignKey("messages.id"))

    message: Mapped["MessageModel"] = relationship(back_populates="attachment")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}