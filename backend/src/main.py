import logging
from contextlib import asynccontextmanager

import routes
from database import create_db_and_tables
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database")
    create_db_and_tables()
    yield
    logger.info("Shutting Down")


app = FastAPI(lifespan=lifespan, root_path="/api")

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


app.include_router(routes.router)

# TODO: add this later
# async def authenticate_user(api_key: str = Security(header_scheme)) -> User:
#     with Session(engine) as session:
#         query = select(User).where(User.api_key == api_key)
#     user = session.exec(query).first()
#     if user is None:
#         raise HTTPException(status_code=403, detail="Could not validate API key")
#     return user


# app.include_router(users.router, prefix="/users", tags=["User"])

# @app.get("/users", response_model=list[UserPublic], tags=["Users"])
# async def read_users():
#     with Session(engine) as session:
#         users = session.exec(select(User)).all()
#         return users


# @app.get("/users/{user_id}", response_model=UserPublic, tags=["Users"])
# async def read_user(user_id: int):
#     with Session(engine) as session:
#         user = session.get(User, user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
#         return user


# @app.get(
#     "/users/{user_id}/annotations",
#     response_model=list[AnnotationPublic],
#     tags=["Users"],
# )
# async def read_user_annotations(user_id: int):
#     with Session(engine) as session:
#         user = session.get(User, user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         query = select(Annotation).where(Annotation.creator_id == user_id)
#         annotations = session.exec(query).all()
#         return annotations


# @app.get("/users/{user_id}/issues", response_model=list[IssuePublic], tags=["Users"])
# async def read_user_issues(user_id: int):
#     with Session(engine) as session:
#         user = session.get(User, user_id)
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")

#         query = select(Issue).where(Issue.creator_id == user_id)
#         issues = session.exec(query).all()
#         return issues


# @app.post("/users")
# async def create_user(user: UserCreate):
#     with Session(engine) as session:
#         session.add(user)
#         session.commit()


# @app.get("/annotations", response_model=list[AnnotationPublic], tags=["Annotations"])
# async def read_annotations():
#     with Session(engine) as session:
#         annotations = session.exec(select(Annotation)).all()
#         return annotations


# @app.get(
#     "/annotations/{annotation_id}",
#     response_model=AnnotationPublic,
#     tags=["Annotations"],
# )
# async def read_annotation(annotation_id: int):
#     with Session(engine) as session:
#         annotation = session.get(Annotation, annotation_id)
#         if not annotation:
#             raise HTTPException(status_code=404, detail="Annotation not found")
#         return annotation


# @app.post("/annotations")
# async def create_annotation(annotation: AnnotationCreate):
#     with Session(engine) as session:
#         if not annotation.creator_id:
#             raise HTTPException(status_code=422, detail="Cannot have null creator id")
#         creator = session.get(User, annotation.creator_id)
#         if not creator:
#             raise HTTPException(status_code=404, detail="Creator not found")

#         if not annotation.problem_id:
#             raise HTTPException(status_code=422, detail="Cannot have null problem id")
#         problem = session.get(Problem, annotation.problem_id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         session.add(annotation)
#         session.commit()


# @app.get("/issues", response_model=list[IssuePublic], tags=["Issues"])
# async def read_issues():
#     with Session(engine) as session:
#         issues = session.exec(select(Issue)).all()
#         return issues


# @app.get("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
# async def read_issue(issue_id: int):
#     with Session(engine) as session:
#         issue = session.get(Issue, issue_id)
#         if not issue:
#             raise HTTPException(status_code=404, detail="Issue not found")
#         return issue


# @app.post("/issues")
# async def create_issue(issue: IssueCreate):
#     with Session(engine) as session:
#         if not issue.creator_id:
#             raise HTTPException(status_code=422, detail="Cannot have null creator id")
#         creator = session.get(User, issue.creator_id)
#         if not creator:
#             raise HTTPException(status_code=404, detail="Creator not found")

#         if not issue.problem_id:
#             raise HTTPException(status_code=422, detail="Cannot have null problem id")
#         problem = session.get(Problem, issue.problem_id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         session.add(issue)
#         session.commit()


# @app.get("/problems", response_model=list[ProblemPublic], tags=["Problems"])
# async def read_problems():
#     with Session(engine) as session:
#         problems = session.exec(select(Problem)).all()
#         return problems


# @app.get("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
# async def read_problem(problem_id: int):
#     with Session(engine) as session:
#         problem = session.get(Problem, problem_id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")
#         return problem


# @app.post("/problems")
# async def create_problem(problem: ProblemCreate):
#     with Session(engine) as session:
#         if not problem.dataset_id:
#             raise HTTPException(status_code=422, detail="Cannot have null dataset id")

#         dataset = session.get(Dataset, problem.dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         session.add(problem)
#         session.commit()


# @app.get("/problems/{problem_id}/annotations", tags=["Problems"])
# async def read_problem_annotations():
#     pass


# @app.get("/problems/{problem_id}/issues", tags=["Problems"])
# async def read_problem_issues():
#     pass


# @app.post("/problems/{problem_id}/annotations")
# async def create_problem_annotation(problem_id: int, annotation: AnnotationCreate):
#     with Session(engine) as session:
#         problem = session.get(Problem, problem_id)
#         if not problem:
#             raise HTTPException(status_code=404, detail="Problem not found")

#         if not annotation.creator_id:
#             raise HTTPException(status_code=422, detail="Cannot have null creator id")
#         creator = session.get(User, annotation.creator_id)
#         if not creator:
#             raise HTTPException(status_code=404, detail="Creator not found")

#         annotation.problem_id = problem_id
#         session.add(annotation)
#         session.commit()


# @app.get("/datasets", response_model=list[DatasetPublic], tags=["Datasets"])
# async def read_datasets():
#     with Session(engine) as session:
#         datasets = session.exec(select(Dataset)).all()
#         return datasets


# @app.get("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
# async def read_dataset(dataset_id: int):
#     with Session(engine) as session:
#         dataset = session.get(Dataset, dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")
#         return dataset


# @app.get(
#     "/datasets/{dataset_id}/problems",
#     response_model=list[ProblemPublic],
#     tags=["Datasets"],
# )
# async def read_dataset_problems(dataset_id: int):
#     with Session(engine) as session:
#         dataset = session.get(Dataset, dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         query = select(Problem).where(Problem.dataset_id == dataset_id)
#         problems = session.exec(query).all()
#         return problems


# @app.post("/datasets")
# async def create_dataset(dataset: DatasetCreate):
#     with Session(engine) as session:
#         session.add(dataset)
#         session.commit()


# @app.post("/datasets/{dataset_id}/problems")
# async def create_dataset_problem(dataset_id: int, problem: ProblemCreate):
#     with Session(engine) as session:
#         dataset = session.get(Dataset, dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")

#         problem.dataset_id = dataset_id
#         session.add(problem)
#         session.commit()


# @app.get("/datasets/{dataset_id}", response_model=UserPublic)
# async def read_dataset(dataset_id: int):
#     with Session(engine) as session:
#         dataset = session.get(Dataset, dataset_id)
#         if not dataset:
#             raise HTTPException(status_code=404, detail="Dataset not found")
#         return dataset


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
