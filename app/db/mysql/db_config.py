from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from global_variables import MYSQL_DB_USER, MYSQL_DB_PASSWORD, MYSQL_DB_HOST, MYSQL_DB_PORT, MYSQL_DB_NAME

db_config = {
    "user": MYSQL_DB_USER,
    "password": MYSQL_DB_PASSWORD,
    "host": MYSQL_DB_HOST,
    "port": MYSQL_DB_PORT,
    "database": MYSQL_DB_NAME
}

SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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