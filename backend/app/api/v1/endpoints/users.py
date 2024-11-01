from app.api.dependencies import get_api_user, get_session
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.annotation import AnnotationPublic
from app.schemas.dataset import DatasetPublic
from app.schemas.issue import IssuePublic
from app.schemas.problem import ProblemPublic
from app.schemas.user import UserCreate, UserPublic, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(
    *,
    user_create: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserPublic:
    user = CRUDUser(session).create(user_create)
    return user


@router.get("/", response_model=list[UserPublic])
def read_users(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[UserPublic]:
    users = CRUDUser(session).read_all()
    return users


@router.get("/{user_id}", response_model=UserPublic)
def read_user(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserPublic:
    user = CRUDUser(session).read(user_id)
    return user


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *,
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserPublic:
    user = CRUDUser(session).update(user_id, user_update)
    return user


@router.delete("/{user_id}")
def delete_user(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
):
    CRUDUser(session).delete(user_id)


@router.get("/{user_id}/users", response_model=list[UserPublic])
def read_user_users(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[UserPublic]:
    pass


@router.get("/{user_id}/annotations", response_model=list[AnnotationPublic])
def read_user_annotations(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationPublic]:
    pass


@router.get("/{user_id}/problems", response_model=list[ProblemPublic])
def read_user_problems(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[ProblemPublic]:
    pass


@router.get("/{user_id}/datasets", response_model=list[DatasetPublic])
def read_user_datasets(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[DatasetPublic]:
    pass


@router.get("/{user_id}/issues", response_model=list[IssuePublic])
def read_user_issues(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssuePublic]:
    pass
