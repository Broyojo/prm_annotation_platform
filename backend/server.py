import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from database import Annotation, Dataset, Problem, User
from fastapi import Depends, FastAPI, HTTPException, Query, Security
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
    engine = create_engine("sqlite:///test_database.db")
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api")
async def index():
    return "hi, please use the api routes :)"


async def authenticate_user(api_key: str = Security(header_scheme)) -> User:
    with Session(engine) as session:
        query = select(User).where(User.api_key == api_key)
    user = session.exec(query).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return user


@app.get("/api/datasets")
async def get_datasets(user: User = Depends(authenticate_user)) -> list[Dataset]:
    with Session(engine) as session:
        query = select(Dataset)
        return list(session.exec(query))


@app.get("/api/datasets/{dataset_id}")
async def get_dataset(
    dataset_id: int, user: User = Depends(authenticate_user)
) -> Dataset:
    with Session(engine) as session:
        dataset = session.get(Dataset, dataset_id)
        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")
        return dataset


@app.get("/api/datasets/{dataset_id}/problems")
async def get_problems(
    dataset_id: int, user: User = Depends(authenticate_user)
) -> list[Problem]:
    with Session(engine) as session:
        query = select(Problem).where(Problem.dataset_id == dataset_id)
        return list(session.exec(query))


@app.get("/api/datasets/{dataset_id}/problems/{problem_index}")
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


class ProblemCreate(BaseModel):
    question: str
    answer: str
    llm_answer: str
    steps: (
        dict[int, str] | list[str]
    )  # user can either submit dict or list of steps (either empty or fully labeled)
    is_correct: Optional[bool] = None
    solve_ratio: Optional[float] = None
    llm_name: Optional[str] = None
    prompt_format: Optional[str] = None
    final_answer: Optional[dict] = None
    extra_metadata: dict = {}


class DatasetCreate(BaseModel):
    name: str
    description: str
    domain: str
    extra_metadata: dict
    problems: list[ProblemCreate]


@app.post("/api/datasets")
async def create_dataset(
    dataset: DatasetCreate, user: User = Depends(authenticate_user)
) -> Dataset:
    with Session(engine) as session:
        new_dataset = Dataset(
            name=dataset.name,
            domain=dataset.domain,
            creator_id=user.id,
            upload_date=datetime.now(),
            description=dataset.description,
            extra_metadata=json.dumps(dataset.extra_metadata),
        )
        session.add(new_dataset)
        session.flush()

        for problem_data in dataset.problems:
            steps = (
                {i: step for i, step in enumerate(problem_data.steps)}
                if type(problem_data.steps) == list
                else problem_data.steps
            )

            problem = Problem(
                dataset_id=new_dataset.id,
                question=problem_data.question,
                answer=problem_data.answer,
                llm_answer=problem_data.llm_answer,
                steps=json.dumps(steps),
                num_steps=len(problem_data.steps),
                is_correct=problem_data.is_correct,
                solve_ratio=problem_data.solve_ratio,
                llm_name=problem_data.llm_name,
                prompt_format=problem_data.prompt_format,
                final_answer=(
                    json.dumps(problem_data.final_answer)
                    if problem_data.final_answer
                    else None
                ),
                extra_metadata=json.dumps(problem_data.extra_metadata),
            )
            session.add(problem)

        try:
            session.commit()
            session.refresh(new_dataset)
            return new_dataset
        except Exception as e:
            session.rollback()
            raise HTTPException(
                status_code=400, detail=f"Failed to create dataset: {str(e)}"
            )
