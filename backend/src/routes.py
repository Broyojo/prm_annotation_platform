from datetime import datetime

from auth import authenticate_user
from database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    Annotation,
    AnnotationCreate,
    AnnotationPublic,
    Dataset,
    DatasetCreate,
    DatasetPublic,
    Issue,
    IssueCreate,
    IssuePublic,
    Problem,
    ProblemCreate,
    ProblemPublic,
    User,
    UserCreate,
    UserPublic,
)
from sqlmodel import Session, select

router = APIRouter()


# Annotation routes
@router.get("/annotations", response_model=list[AnnotationPublic], tags=["Annotations"])
async def read_annotations(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Annotation)).all()


@router.post("/annotations", response_model=AnnotationPublic, tags=["Annotations"])
async def create_annotation(
    annotation: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get(
    "/annotations/{annotation_id}",
    response_model=AnnotationPublic,
    tags=["Annotations"],
)
async def read_annotation(
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    annotation = session.get(Annotation, annotation_id)
    if not annotation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found"
        )
    return annotation


@router.patch(
    "/annotations/{annotation_id}",
    response_model=AnnotationPublic,
    tags=["Annotations"],
)
async def update_annotation(
    annotation_id: int,
    annotation: AnnotationCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.put(
    "/annotations/{annotation_id}",
    response_model=AnnotationPublic,
    tags=["Annotations"],
)
async def overwrite_annotation(
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.delete("/annotations/{annotation_id}", tags=["Annotations"])
async def delete_annotation(
    annotation_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


# Dataset routes
@router.get("/datasets", response_model=list[DatasetPublic], tags=["Datasets"])
async def read_datasets(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Dataset)).all()


@router.post("/datasets", response_model=DatasetPublic, tags=["Datasets"])
async def create_dataset(
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    db_dataset = dataset.to_db_model(api_user.id)
    session.add(db_dataset)
    session.commit()
    session.refresh(db_dataset)
    return DatasetPublic(**db_dataset.__dict__)


@router.get("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
async def read_dataset(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )
    return DatasetPublic(**dataset.__dict__)


@router.patch("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
async def update_dataset(
    dataset_id: int,
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.put("/datasets/{dataset_id}", response_model=DatasetPublic, tags=["Datasets"])
async def overwrite_dataset(
    dataset_id: int,
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.delete("/datasets/{dataset_id}", tags=["Datasets"])
async def delete_dataset(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


# Issue routes
@router.get("/issues", response_model=list[IssuePublic], tags=["Issues"])
async def read_issues(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Issue)).all()


@router.post("/issues", response_model=IssuePublic, tags=["Issues"])
async def create_issue(
    issue: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
async def read_issue(
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    issue = session.get(Issue, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Issue not found"
        )
    return issue


@router.patch("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
async def update_issue(
    issue_id: int,
    issue: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.put("/issues/{issue_id}", response_model=IssuePublic, tags=["Issues"])
async def overwrite_issue(
    issue_id: int,
    issue: IssueCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.delete("/issues/{issue_id}", tags=["Issues"])
async def delete_issue(
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


# Problem routes
@router.get("/problems", response_model=list[ProblemPublic], tags=["Problems"])
async def read_problems(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Problem)).all()


@router.post("/problems", response_model=ProblemPublic, tags=["Problems"])
async def create_problem(
    problem: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
async def read_problem(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    return problem


@router.patch("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
async def update_problem(
    problem_id: int,
    problem: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.put("/problems/{problem_id}", response_model=ProblemPublic, tags=["Problems"])
async def overwrite_problem(
    problem_id: int,
    problem: ProblemCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.delete("/problems/{problem_id}", tags=["Problems"])
async def delete_problem(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


# User routes
@router.get("/users", response_model=list[UserPublic], tags=["Users"])
async def read_users(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(User)).all()


@router.post("/users", response_model=UserPublic, tags=["Users"])
async def create_user(
    user: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> UserPublic:
    if api_user.permissions != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non-admin user cannot add new user",
        )

    db_user = User(
        **user.model_dump(),
        created_at=datetime.now(),
        last_modified=datetime.now(),
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserPublic(**db_user.__dict__)


@router.get("/users/{user_id}", response_model=UserPublic, tags=["Users"])
async def read_user(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/users/{user_id}", response_model=UserPublic, tags=["Users"])
async def update_user(
    user_id: int,
    user: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.put("/users/{user_id}", response_model=UserPublic, tags=["Users"])
async def overwrite_user(
    user_id: int,
    user: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.delete("/users/{user_id}", tags=["Users"])
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


# Relationship routes
@router.get(
    "/datasets/{dataset_id}/problems",
    response_model=list[ProblemPublic],
    tags=["Datasets"],
)
async def read_dataset_problems(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if session.get(Dataset, dataset_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found"
        )
    query = select(Problem).where(Problem.dataset_id == dataset_id)
    problems = session.exec(query).all()
    return problems


@router.get(
    "/datasets/{dataset_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Datasets"],
)
async def read_dataset_annotations(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get(
    "/datasets/{dataset_id}/issues", response_model=list[IssuePublic], tags=["Datasets"]
)
async def read_dataset_issues(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    pass


@router.get(
    "/problems/{problem_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Problems"],
)
async def read_problem_annotations(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(Problem, problem_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    query = select(Annotation).where(Annotation.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations


@router.get(
    "/problems/{problem_id}/issues", response_model=list[IssuePublic], tags=["Problems"]
)
async def read_problem_issues(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(Problem, problem_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Problem not found"
        )
    query = select(Issue).where(Issue.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations


@router.get(
    "/users/{user_id}/annotations",
    response_model=list[AnnotationPublic],
    tags=["Users"],
)
async def read_user_annotations(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(User, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    annotations = session.exec(
        select(Annotation).where(Annotation.creator_id == user_id)
    ).all()
    return annotations


@router.get("/users/{user_id}/issues", response_model=list[IssuePublic], tags=["Users"])
async def read_user_issues(
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(User, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    issues = session.exec(select(Issue).where(Issue.creator_id == user_id)).all()
    return issues
