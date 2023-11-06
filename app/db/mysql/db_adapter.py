from contextlib import contextmanager
from sqlalchemy.orm import Session
from .db_config import SessionLocal


class MysqlDBAdapter:
    @contextmanager
    def get_session(self) -> Session:
        session = SessionLocal()
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()
