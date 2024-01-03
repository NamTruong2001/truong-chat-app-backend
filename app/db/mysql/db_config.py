from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()
db_config = {
    "user": settings.mysql_db_user,
    "password": settings.mysql_db_password,
    "host": settings.mysql_db_host,
    "port": settings.mysql_db_port,
    "database": settings.mysql_db_name,
}

ssl_ca = {"ssl_ca": "DigiCertGlobalRootCA.crt.pem"}

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=ssl_ca,
    # echo=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
