import json
import logging
from contextlib import asynccontextmanager
from enum import Enum

from database import Annotation, Dataset, Problem, User
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, select

engine = None

logger = logging.getLogger("uvicorn.error")

header_scheme = APIKeyHeader(name="x-key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine
    logger.info("Loading database")
    engine = create_engine(
        "sqlite:///prmbench_database.db", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan, root_path="/api")

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


async def authenticate_user(api_key: str = Security(header_scheme)) -> User:
    with Session(engine) as session:
        query = select(User).where(User.api_key == api_key)
    user = session.exec(query).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return user


@app.get("/datasets")
async def get_datasets(user: User = Depends(authenticate_user)) -> list[Dataset]:
    with Session(engine) as session:
        query = select(Dataset)
        return list(session.exec(query))


@app.get("/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: int, user: User = Depends(authenticate_user)
) -> Dataset:
    with Session(engine) as session:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset


@app.get("/datasets/{dataset_id}/problems")
async def get_problems(
    dataset_id: int, user: User = Depends(authenticate_user)
) -> list[Problem]:
    with Session(engine) as session:
        query = select(Problem).where(Problem.dataset_id == dataset_id)
        return list(session.exec(query))


@app.get("/datasets/{dataset_id}/problems/{problem_index}")
async def get_problem(
    dataset_id: int, problem_index: int, user: User = Depends(authenticate_user)
) -> dict:
    with Session(engine) as session:
        total_query = select(Problem).where(Problem.dataset_id == dataset_id)
        total_problems = len(list(session.exec(total_query)))

        if problem_index < 0 or problem_index >= total_problems:
            raise HTTPException(status_code=404, detail="Problem not found")

        query = (
            select(Problem)
            .where(Problem.dataset_id == dataset_id)
            .offset(problem_index)
            .limit(1)
        )
        problem = session.exec(query).first()

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        return {"total_problems": total_problems, "problem": problem}


@app.get("/datasets/{dataset_id}/problems/{problem_index}/annotation")
async def get_annotation(
    dataset_id: int, problem_index: int, user: User = Depends(authenticate_user)
) -> dict:
    with Session(engine) as session:
        total_query = select(Problem).where(Problem.dataset_id == dataset_id)
        total_problems = len(list(session.exec(total_query)))

        if problem_index < 0 or problem_index >= total_problems:
            raise HTTPException(status_code=404, detail="Problem not found")

        query = (
            select(Problem)
            .where(Problem.dataset_id == dataset_id)
            .offset(problem_index)
            .limit(1)
        )
        problem = session.exec(query).first()

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        # Get annotation for this problem and user
        annotation_query = select(Annotation).where(
            Annotation.problem_id == problem.id, Annotation.user_id == user.id
        )
        annotation = session.exec(annotation_query).first()

        if not annotation:
            return {"annotation": None}

        return {
            "annotation": {
                "id": annotation.id,
                "step_labels": json.loads(annotation.step_labels),
            }
        }


class RatingEnum(str, Enum):
    GOOD = "Good"
    NEUTRAL = "Neutral"
    BAD = "Bad"
    ERROR = "Error"


class AnnotationUpdate(BaseModel):
    step_index: int
    rating: RatingEnum


@app.put("/datasets/{dataset_id}/problems/{problem_index}/annotation")
async def update_annotation(
    dataset_id: int,
    problem_index: int,
    update: AnnotationUpdate,
    user: User = Depends(authenticate_user),
) -> dict:
    with Session(engine) as session:
        try:
            # Get the problem first
            query = (
                select(Problem)
                .where(Problem.dataset_id == dataset_id)
                .offset(problem_index)
                .limit(1)
            )
            problem = session.exec(query).first()

            if not problem:
                raise HTTPException(status_code=404, detail="Problem not found")

            # Find existing annotation or create new one
            annotation_query = select(Annotation).where(
                Annotation.problem_id == problem.id, Annotation.user_id == user.id
            )
            annotation = session.exec(annotation_query).first()

            if annotation:
                # Update existing annotation
                step_labels = (
                    json.loads(annotation.step_labels) if annotation.step_labels else {}
                )
                step_labels[str(update.step_index)] = (
                    update.rating.value
                )  # Use .value to get string
                annotation.step_labels = json.dumps(step_labels)
            else:
                # Create new annotation
                step_labels = {
                    str(update.step_index): update.rating.value
                }  # Use .value to get string
                annotation = Annotation(
                    step_labels=json.dumps(step_labels),
                    problem_id=problem.id,
                    user_id=user.id,
                )
                session.add(annotation)

            session.commit()

            return {
                "annotation": {
                    "id": annotation.id,
                    "step_labels": json.loads(annotation.step_labels),
                }
            }
        except Exception as e:
            session.rollback()
            raise e
