
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.settings import settings

#заменить на DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL_LOCAL,
    connect_args={"options": "-c search_path=ideabridge,public"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # create schema and tables if not exists (for dev; in prod use alembic)
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS ideabridge"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
