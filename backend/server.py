import logging
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum

import orjson
from database import Annotation, Dataset, Problem, User, download_database
from fastapi import Depends, FastAPI, HTTPException, Response, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy import text
from utils import report_timestamp, model_answer_step_merging, sqlmodel_query2str
import pdb

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
    expose_headers=["Content-Disposition"],
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

        # 'SELECT problem.id, problem.question, problem.answer, 
        # problem.model_answer, problem.model_answer_steps, problem.is_correct, 
        # problem.solve_ratio, problem.model_name, problem.prompt_format, 
        # problem.final_answer, problem.dataset_id 
        # FROM problem WHERE problem.dataset_id = 5\n LIMIT 1 OFFSET 0'
        query = (
            select(Problem)
            .where(Problem.dataset_id == dataset_id)
            .offset(problem_index)
            .limit(1)
        )
        problem = session.exec(query).first()

        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")

        model_answer_steps = orjson.loads(problem.model_answer_steps)
        model_answer_steps, annotation_step_merge, annotation_step_label_heritage = model_answer_step_merging(model_answer_steps)
        problem.model_answer_steps = orjson.dumps(model_answer_steps).decode('utf-8')

        # annotation from all users
        all_user_annotations = problem.annotations

        for user_idx, user_annotation in enumerate(all_user_annotations):
            user_step_labels_updated = {}
            user_step_labels = orjson.loads(user_annotation.step_labels)
            for step_idx, label_step_idx in annotation_step_label_heritage.items():
                if str(label_step_idx) in user_step_labels:
                    user_step_labels_updated[str(step_idx)] = user_step_labels[str(label_step_idx)]
            user_annotation.step_labels = orjson.dumps(user_step_labels_updated).decode('utf-8')
            problem.annotations[user_idx] = user_annotation

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

        # Update the latest start time of problem
        step_labels = orjson.loads(annotation.step_labels)
        time_stamp = report_timestamp()
        for step_idx, step_label in step_labels.items():
            if isinstance(step_label, str):
                step_label = {
                            "label": step_label,
                            "time_created": "NotRecored",
                            "time_last_update": "NotRecored",
                            "time_last_start": time_stamp,
                            "num_revision": 0
                        }
            else:
                step_label["time_last_start"] = time_stamp
            step_labels[step_idx] = step_label

        return {
            "annotation": {
                "id": annotation.id,
                "step_labels": step_labels,
            }
        }


class RatingEnum(str, Enum):
    GOOD = "Good"
    NEUTRAL = "Neutral"
    BAD = "Bad"
    ERROR = "Error Realization"


class AnnotationUpdate(BaseModel):
    step_index: int
    rating: RatingEnum


@app.put("/datasets/{dataset_id}/problems/{problem_index}/annotation")
async def update_annotation(
    dataset_id: int,
    problem_index: int,
    updates: list[AnnotationUpdate],
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
                    orjson.loads(annotation.step_labels)
                    if annotation.step_labels
                    else {}
                )

                for update in updates:
                    step_index_key = str(update.step_index)
                    if step_index_key in step_labels and \
                        isinstance(step_labels[step_index_key], str):
                        step_labels[step_index_key] = {
                            "label": step_labels[step_index_key],
                            "time_created": "NotRecored",
                            "time_last_update": "NotRecored",
                            "num_revision": 0
                        }
                    elif step_index_key in step_labels:
                        time_stamp = report_timestamp()
                        step_labels[step_index_key]["label"] = update.rating.value
                        if "timestamp_created" not in step_labels[step_index_key]:
                            step_labels[step_index_key]["timestamp_created"] = time_stamp
                        step_labels[step_index_key]["time_last_update"] = time_stamp
                        step_labels[step_index_key]["num_revision"] = step_labels[step_index_key].get("num_revision", -1) + 1
                    else:
                        time_stamp = report_timestamp()
                        step_labels[step_index_key] = {
                            "label": update.rating.value,
                            "time_created": time_stamp,
                            "time_last_update": time_stamp,
                            "num_revision": 0
                        }

                annotation.step_labels = orjson.dumps(step_labels).decode("utf-8")
            else:
                # Create new annotation
                time_stamp = report_timestamp()
                step_labels = {
                    str(update.step_index): {"label": update.rating.value,
                                             "time_created": time_stamp,
                                             "time_last_update": time_stamp,
                                             "num_revision": 0} for update in updates
                }

                annotation = Annotation(
                    step_labels=orjson.dumps(step_labels).decode("utf-8"),
                    problem_id=problem.id,
                    user_id=user.id,
                )
                session.add(annotation)

            session.commit()
            return {
                "annotation": {
                    "id": annotation.id,
                    "step_labels": orjson.loads(annotation.step_labels),
                }
            }
        except Exception as e:
            session.rollback()
            print("Annotation Error:")
            raise e


@app.get("/export")
async def export_database(user: User = Depends(authenticate_user)):
    if user.access in ["admin", "dev"]:
        try:
            output = download_database(engine=engine)
            json_content = orjson.dumps(output)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"database_export_{timestamp}.json"
            response = Response(content=json_content, media_type="application/json")
            response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
            response.headers["Content-Length"] = str(len(json_content))
            return response
        except Exception as e:
            return JSONResponse(
                status_code=500, content={"error": f"Failed to export database: {str(e)}"}
            )
