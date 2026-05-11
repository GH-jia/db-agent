import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DB_HOST = "172.16.1.20"
DB_PORT = 18247
DB_NAME = "demo"
DB_USER = "admin"
DB_PASSWORD = os.getenv("DB_PASSWORD", "aa7062bd")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
