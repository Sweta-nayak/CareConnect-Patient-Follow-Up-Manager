
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


# Create MySQL database URL

database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME
)


# Create database engine

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=3600
)


# Create database session

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# Base class for database models

class Base(DeclarativeBase):
    pass


# Database dependency

def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
