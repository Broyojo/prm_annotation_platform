import logging
from contextlib import asynccontextmanager

from database import Annotation, Dataset, Problem, User
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyCookie, APIKeyHeader
from sqlmodel import Session, SQLModel, create_engine, select

engine = None

logger = logging.getLogger("uvicorn.error")

cookie_scheme = APIKeyCookie(name="session")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("Running startup code")
    engine = create_engine("sqlite:///test_database.db")
    SQLModel.metadata.create_all(engine)
    yield
    logger.info("Running cleanup code")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def index():
    users = []
    with Session(engine) as session:
        problems = session.exec(
            select(Problem).where(
                Problem.solve_ratio is not None and Problem.solve_ratio < 0.1
            )
        )
        for problem in problems:
            for annotation in problem.annotations:
                users.append(annotation.user.name)
    return users


@app.get("/items/")
async def read_items(session: str = Depends(cookie_scheme)):
    return {"session": session}


async def get_api_user(api_key: str = Security(cookie_scheme)) -> User:
    with Session(engine) as session:
        query = select(User).where(User.api_key == api_key)
    user = session.exec(query).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return user


async def login():
    pass


@app.get("/datasets")
async def get_datasets(user: User = Depends(get_api_user)) -> list[Dataset]:
    with Session(engine) as session:
        query = select(Dataset)
        return list(session.exec(query))


@app.get("/users")
async def get_users() -> list[User]:
    with Session(engine) as session:
        query = select(User)
        return list(session.exec(query))
