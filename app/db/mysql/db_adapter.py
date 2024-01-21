from contextlib import contextmanager
from sqlalchemy.orm import Session
from .db_config import SessionLocal


class MysqlDBAdapter:
    def get_session(self) -> Session:
        pass



class OneConnectionPerRequestMysqlDBAdapter(MysqlDBAdapter):
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


class OneConnectionOnlyMysqlDBAdapter(MysqlDBAdapter):
    def __init__(self, session):
        self.session = session

    @contextmanager
    def get_session(self) -> Session:
        try:
            yield self.session
        except:
            self.session.rollback()
            raise
        finally:
            self.session.close()
