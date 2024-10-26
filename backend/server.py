import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import APIKeyHeader
from models import Annotation, Comment, Dataset, Problem, User
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, distinct, func, select

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


@app.get("/", include_in_schema=False)
async def index():
    return RedirectResponse(url="/docs")


@app.get("/api", include_in_schema=False)
async def api_index():
    return RedirectResponse(url="/docs")


async def authenticate_user(api_key: str = Security(header_scheme)) -> User:
    with Session(engine) as session:
        query = select(User).where(User.api_key == api_key)
    user = session.exec(query).first()
    if user is None:
        raise HTTPException(status_code=403, detail="Could not validate API key")
    return user


async def get_statistics(dataset_id: int) -> Stats:
    pass


# class DatasetWithStats(BaseModel):
#     dataset: Dataset
#     total_problems: int
#     problems_with_annotations: int
#     total_comments: int


# async def get_datasets(
#     user: User = Depends(authenticate_user),
# ) -> list[DatasetWithStats]:
#     with Session(engine) as session:
#         datasets = session.exec(select(Dataset)).all()

#         results = []

#         for dataset in datasets:
#             stats = session.exec(
#                 select(
#                     func.count(distinct(Problem.id)).label("total_problems"),
#                     func.count(distinct(Problem.id))
#                     .select_from(Problem)
#                     .join(Annotation)
#                     .where(Problem.dataset_id == dataset.id)
#                     .label("problems_with_annotations"),
#                     func.count(distinct(Comment.id)).label("total_comments"),
#                 )
#                 .select_from(Problem)
#                 .outerjoin(Comment)
#                 .where(Problem.dataset_id == dataset.id)
#             ).first()

#             if not stats:
#                 return []

#             results.append(
#                 DatasetWithStats(
#                     dataset=dataset,
#                     total_problems=stats[0] or 0,
#                     problems_with_annotations=stats[1] or 0,
#                     total_comments=stats[2] or 0,
#                 )
#             )

#         return results


# class ProblemCreate(BaseModel):
#     question: str
#     answer: str
#     llm_answer: str
#     steps: dict[int, str] | list[str]
#     is_correct: Optional[bool] = None
#     solve_ratio: Optional[float] = None
#     llm_name: Optional[str] = None
#     prompt_format: Optional[str] = None
#     final_answer: Optional[dict] = None
#     extra_metadata: dict = {}


# class DatasetCreate(BaseModel):
#     name: str
#     description: str
#     domain: str
#     extra_metadata: dict
#     problems: list[ProblemCreate]


# @app.post("/api/datasets")
# async def create_dataset(
#     dataset: DatasetCreate, user: User = Depends(authenticate_user)
# ):
#     pass


# @app.put("/api/datasets")
# async def update_dataset():
#     pass


# @app.post("/api/datasets/{datasets_id}/problems")
# async def create_problems(dataset_id: int, problems: list[ProblemCreate]):
#     pass


# @app.put("/api/problems/{problem_id}")
# async def update_problem(problem_id: int, problem: ProblemCreate):
#     pass


# @app.get("/api/datasets")
# async def get_datasets(
#     user: User = Depends(authenticate_user),
# ) -> list[DatasetWithStats]:
#     with Session(engine) as session:
#         query = select(Dataset)
#         l = list(session.exec(query))


# @app.get("/api/datasets/{dataset_id}")
# async def get_dataset(
#     dataset_id: int, user: User = Depends(authenticate_user)
# ) -> Dataset:
#     with Session(engine) as session:
#         dataset = session.get(Dataset, dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")
#         return dataset


# @app.get("/api/datasets/{dataset_id}/problems")
# async def get_problems(
#     dataset_id: int, user: User = Depends(authenticate_user)
# ) -> list[Problem]:
#     with Session(engine) as session:
#         query = select(Problem).where(Problem.dataset_id == dataset_id)
#         return list(session.exec(query))


# @app.get("/api/datasets/{dataset_id}/problems/{problem_index}")
# async def get_problem(
#     dataset_id: int, problem_index: int, user: User = Depends(authenticate_user)
# ) -> dict:
#     with Session(engine) as session:
#         total_query = select(Problem).where(Problem.dataset_id == dataset_id)
#         total_problems = len(list(session.exec(total_query)))

#         if problem_index < 0 or problem_index >= total_problems:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         query = (
#             select(Problem)
#             .where(Problem.dataset_id == dataset_id)
#             .offset(problem_index)
#             .limit(1)
#         )
#         problem = session.exec(query).first()

#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         return {"total_problems": total_problems, "problem": problem}


# class ProblemCreate(BaseModel):
#     id: Optional[int] = None  # Add optional ID for existing problems
#     question: str
#     answer: str
#     llm_answer: str
#     steps: dict[int, str] | list[str]
#     is_correct: Optional[bool] = None
#     solve_ratio: Optional[float] = None
#     llm_name: Optional[str] = None
#     prompt_format: Optional[str] = None
#     final_answer: Optional[dict] = None
#     extra_metadata: dict = {}


# class DatasetCreate(BaseModel):
#     id: Optional[int] = None
#     name: str
#     description: str
#     domain: str
#     extra_metadata: dict
#     problems: list[ProblemCreate]


# @app.post("/api/datasets")
# async def create_dataset(
#     dataset: DatasetCreate, user: User = Depends(authenticate_user)
# ) -> Dataset:
#     with Session(engine) as session:
#         if dataset.id is not None:
#             existing_dataset = session.get(Dataset, dataset.id)
#             if existing_dataset:
#                 existing_dataset.name = dataset.name
#                 existing_dataset.domain = dataset.domain
#                 existing_dataset.description = dataset.description
#                 existing_dataset.extra_metadata = json.dumps(dataset.extra_metadata)
#                 existing_dataset.last_modified = datetime.now()
#                 new_dataset = existing_dataset
#             else:
#                 new_dataset = Dataset(
#                     id=dataset.id,
#                     name=dataset.name,
#                     domain=dataset.domain,
#                     creator_id=user.id,
#                     created_at=datetime.now(),
#                     description=dataset.description,
#                     extra_metadata=json.dumps(dataset.extra_metadata),
#                     last_modified=datetime.now(),
#                 )
#                 session.add(new_dataset)
#         else:
#             new_dataset = Dataset(
#                 name=dataset.name,
#                 domain=dataset.domain,
#                 creator_id=user.id,
#                 created_at=datetime.now(),
#                 description=dataset.description,
#                 extra_metadata=json.dumps(dataset.extra_metadata),
#                 last_modified=datetime.now(),
#             )
#             session.add(new_dataset)

#         session.flush()

#         processed_problem_ids = set()

#         for problem_data in dataset.problems:
#             steps = (
#                 {i: step for i, step in enumerate(problem_data.steps)}
#                 if isinstance(problem_data.steps, list)
#                 else problem_data.steps
#             )

#             if problem_data.id is not None:
#                 existing_problem = session.get(Problem, problem_data.id)
#                 if existing_problem and existing_problem.dataset_id == new_dataset.id:
#                     existing_problem.question = problem_data.question
#                     existing_problem.answer = problem_data.answer
#                     existing_problem.llm_answer = problem_data.llm_answer
#                     existing_problem.steps = json.dumps(steps)
#                     existing_problem.num_steps = len(problem_data.steps)
#                     existing_problem.is_correct = problem_data.is_correct
#                     existing_problem.solve_ratio = problem_data.solve_ratio
#                     existing_problem.llm_name = problem_data.llm_name
#                     existing_problem.prompt_format = problem_data.prompt_format
#                     existing_problem.final_answer = (
#                         json.dumps(problem_data.final_answer)
#                         if problem_data.final_answer
#                         else None
#                     )
#                     existing_problem.extra_metadata = json.dumps(
#                         problem_data.extra_metadata
#                     )
#                     existing_problem.last_modified = datetime.now()
#                     processed_problem_ids.add(existing_problem.id)
#                     continue

#             new_problem = Problem(
#                 id=problem_data.id,
#                 dataset_id=new_dataset.id,
#                 question=problem_data.question,
#                 answer=problem_data.answer,
#                 llm_answer=problem_data.llm_answer,
#                 steps=json.dumps(steps),
#                 num_steps=len(problem_data.steps),
#                 is_correct=problem_data.is_correct,
#                 solve_ratio=problem_data.solve_ratio,
#                 llm_name=problem_data.llm_name,
#                 prompt_format=problem_data.prompt_format,
#                 final_answer=(
#                     json.dumps(problem_data.final_answer)
#                     if problem_data.final_answer
#                     else None
#                 ),
#                 extra_metadata=json.dumps(problem_data.extra_metadata),
#                 created_at=datetime.now(),
#                 last_modified=datetime.now(),
#             )
#             session.add(new_problem)
#             if new_problem.id:
#                 processed_problem_ids.add(new_problem.id)

#         if dataset.id is not None:
#             query = select(Problem).where(Problem.dataset_id == dataset.id)
#             existing_problems = session.exec(query)
#             for problem in existing_problems:
#                 if problem.id not in processed_problem_ids:
#                     session.delete(problem)

#         try:
#             session.commit()
#             session.refresh(new_dataset)
#             return new_dataset
#         except Exception as e:
#             session.rollback()
#             raise HTTPException(
#                 status_code=400, detail=f"Failed to create/update dataset: {str(e)}"
#             )


# StepLabelType = Literal["Good", "Bad", "Neutral", "Error Realization"]


# class StepLabelUpdate(BaseModel):
#     index: int
#     label: Optional[StepLabelType] = None


# class AnnotationResponse(BaseModel):
#     message: str
#     step_labels: dict[str, StepLabelType]
#     total_steps: int
#     last_modified: datetime


# @app.post("/api/problems/{problem_id}/annotations", response_model=AnnotationResponse)
# async def update_annotation(
#     problem_id: int,
#     step_label: StepLabelUpdate,
#     user: User = Depends(authenticate_user),
# ) -> dict:
#     with Session(engine) as session:
#         problem = session.get(Problem, problem_id)
#         if not problem:
#             raise HTTPException(
#                 status_code=404, detail=f"Problem {problem_id} not found"
#             )

#         if step_label.index < 0 or step_label.index >= problem.num_steps:
#             raise HTTPException(
#                 status_code=400,
#                 detail=f"Step index {step_label.index} out of range for problem with {problem.num_steps} steps",
#             )

#         query = select(Annotation).where(
#             Annotation.problem_id == problem_id, Annotation.user_id == user.id
#         )
#         annotation = session.exec(query).first()

#         if annotation:
#             try:
#                 step_labels = json.loads(annotation.step_labels)
#             except json.JSONDecodeError:
#                 step_labels = {}
#         else:
#             step_labels = {}
#             annotation = Annotation(
#                 problem_id=problem_id,
#                 user_id=user.id,
#                 step_labels=json.dumps(step_labels),
#                 created_at=datetime.now(),
#                 last_modified=datetime.now(),
#             )
#             session.add(annotation)

#         if step_label.label is None:
#             step_labels.pop(str(step_label.index), None)
#         else:
#             step_labels[str(step_label.index)] = step_label.label

#         annotation.step_labels = json.dumps(step_labels)
#         annotation.last_modified = datetime.now()

#         try:
#             session.commit()
#             return {
#                 "message": "Annotation updated successfully",
#                 "step_labels": step_labels,
#                 "total_steps": problem.num_steps,
#                 "last_modified": annotation.last_modified,
#             }
#         except Exception as e:
#             session.rollback()
#             raise HTTPException(
#                 status_code=400, detail=f"Failed to update annotation: {str(e)}"
#             )


# @app.get("/api/problems/{problem_id}/annotations", response_model=AnnotationResponse)
# async def get_annotations(
#     problem_id: int, user: User = Depends(authenticate_user)
# ) -> dict:
#     with Session(engine) as session:
#         problem = session.get(Problem, problem_id)
#         if not problem:
#             raise HTTPException(
#                 status_code=404, detail=f"Problem {problem_id} not found"
#             )

#         query = select(Annotation).where(
#             Annotation.problem_id == problem_id, Annotation.user_id == user.id
#         )
#         annotation = session.exec(query).first()

#         if not annotation:
#             return {
#                 "message": "No annotations found",
#                 "step_labels": {},
#                 "total_steps": problem.num_steps,
#                 "last_modified": datetime.now(),
#             }

#         try:
#             step_labels = json.loads(annotation.step_labels)
#         except json.JSONDecodeError:
#             step_labels = {}

#         return {
#             "message": "Annotations retrieved successfully",
#             "step_labels": step_labels,
#             "total_steps": problem.num_steps,
#             "last_modified": annotation.last_modified,
#         }
