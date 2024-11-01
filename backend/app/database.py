import logging

from sqlmodel import Session, SQLModel, create_engine

logger = logging.getLogger("uvicorn.error")

url = "sqlite:///prmbench_database.db"
engine = create_engine(
    url,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
