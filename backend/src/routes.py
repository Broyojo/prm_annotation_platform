from datetime import datetime

from auth import authenticate_user
from database import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from models import (
    Annotation,
    AnnotationPublic,
    Dataset,
    DatasetCreate,
    DatasetPublic,
    Issue,
    IssuePublic,
    Problem,
    ProblemPublic,
    User,
    UserCreate,
    UserPublic,
)
from sqlmodel import Session, select

router = APIRouter(prefix="/api")


@router.get("/annotations", response_model=list[AnnotationPublic], tags=["Annotations"])
async def read_annotations(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Annotation)).all()


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
        raise HTTPException(status_code=404, detail="Annotation not found")
    return annotation


@router.get("/datasets", response_model=list[DatasetPublic])
async def read_datasets(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Dataset)).all()


@router.get("/datasets/{dataset_id}", response_model=DatasetPublic)
async def read_dataset(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    dataset = session.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset not found")

    dataset_public = DatasetPublic(
        **dataset.__dict__,
        creator=dataset.creator,
    )

    return dataset_public


@router.get("/datasets/{dataset_id}/problems", response_model=list[ProblemPublic])
async def read_dataset_problems(
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if session.get(Dataset, dataset_id) is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    query = select(Problem).where(Problem.dataset_id == dataset_id)
    problems = session.exec(query).all()
    return problems


@router.post("/datasets", response_model=DatasetPublic)
async def create_dataset(
    dataset: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
) -> DatasetPublic:
    db_dataset = Dataset(
        **dataset.model_dump(),
        created_at=datetime.now(),
        last_modified=datetime.now(),
    )
    session.add(db_dataset)
    session.commit()
    session.refresh(db_dataset)
    return DatasetPublic(**db_dataset.__dict__)


@router.get("/issues", response_model=list[IssuePublic])
async def read_issues(
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    return session.exec(select(Issue)).all()


@router.get("/issues/{issue_id}", response_model=IssuePublic)
async def read_issue(
    issue_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    issue = session.get(Issue, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue


@router.get("/problems", response_model=list[ProblemPublic])
async def read_problems(
    session: Session = Depends(get_session), api_user: User = Depends(authenticate_user)
):
    problems = session.exec(select(Problem)).all()
    return problems


@router.get("/problems/{problem_id}", response_model=ProblemPublic)
async def read_problem(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    problem = session.get(Problem, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.get("/problems/{problem_id}/annotations")
async def read_problem_annotations(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(Problem, problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    query = select(Annotation).where(Annotation.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations


@router.get("/problems/{problem_id}/issues")
async def read_problem_issues(
    problem_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(authenticate_user),
):
    if not session.get(Problem, problem_id):
        raise HTTPException(status_code=404, detail="Problem not found")
    query = select(Issue).where(Issue.problem_id == problem_id)
    annotations = session.exec(query).all()
    return annotations


@router.get("/users", response_model=list[UserPublic])
async def read_users(
    session: Session = Depends(get_session), api_user: User = Depends(authenticate_user)
):
    return session.exec(select(User)).all()


@router.get("/users/{user_id}", response_model=UserPublic)
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


@router.get("/users/{user_id}/annotations", response_model=list[AnnotationPublic])
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


@router.get("/users/{user_id}/issues", response_model=list[IssuePublic])
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


@router.post("/users", response_model=UserPublic)
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
        **user.model_dump(), created_at=datetime.now(), last_modified=datetime.now()
    )

    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return UserPublic(**db_user.__dict__)
