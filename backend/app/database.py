import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base, sessionmaker


load_dotenv()

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD is not set")

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username="solvigo_app",
    password=POSTGRES_PASSWORD,
    host="localhost",
    port=5432,
    database="solvigo",
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()