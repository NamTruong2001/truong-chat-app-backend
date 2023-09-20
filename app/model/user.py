from sqlalchemy import Column, String, BigInteger, Boolean, DateTime

from db.database import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}



