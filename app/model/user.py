from sqlalchemy import Column, String, BigInteger, Boolean, DateTime
from sqlalchemy.orm import mapped_column
from db.db_config import Base


class UserModel(Base):
    __tablename__ = "users"

    id = mapped_column(BigInteger, primary_key=True, index=True)
    username = mapped_column(String)
    password = mapped_column(String, deferred=True)
    first_name = mapped_column(String)
    last_name = mapped_column(String)
    email = mapped_column(String)
    is_active = mapped_column(Boolean, default=False, deferred=True)
    created_at = mapped_column(DateTime, deferred=True)
    updated_at = mapped_column(DateTime, deferred=True)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



