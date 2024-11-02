import logging

from sqlmodel import Session, SQLModel, create_engine, select

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

url = settings.db_url
engine = create_engine(
    url,
    connect_args={"check_same_thread": False},
)


def create_db_and_tables():
    from app.models.annotation import Annotation
    from app.models.base import ModelBase
    from app.models.dataset import Dataset
    from app.models.issue import Issue
    from app.models.problem import Problem
    from app.models.user import User

    SQLModel.metadata.create_all(engine)

    # add default user
    with Session(engine) as session:
        user = session.exec(select(User).where(User.name == "David Andrews")).first()
        if user is None:
            session.add(User(name="David Andrews", permissions="admin", creator_id=-1))
            session.commit()


def get_session():
    with Session(engine) as session:
        yield session


# TODO: improve this by looking at claude's code
