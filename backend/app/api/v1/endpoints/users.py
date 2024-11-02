from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_api_user, get_session
from app.crud.user import CRUDUser
from app.models.user import User
from app.schemas.annotation import AnnotationRead
from app.schemas.dataset import DatasetRead
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemRead
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_user(
    *,
    user_create: UserCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserRead:
    return CRUDUser(session, api_user).create(user_create)


@router.get("/", response_model=list[UserRead])
def read_users(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[UserRead]:
    return CRUDUser(session, api_user).read_all()


@router.get("/{user_id}", response_model=UserRead)
def read_user(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserRead:
    return CRUDUser(session, api_user).read(user_id)


@router.get("/{user_id}/users", response_model=list[UserRead])
def read_user_users(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[UserRead]:
    return CRUDUser(session, api_user).read_user_users(user_id)


@router.get("/{user_id}/annotations", response_model=list[AnnotationRead])
def read_user_annotations(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationRead]:
    return CRUDUser(session, api_user).read_user_annotations(user_id)


@router.get("/{user_id}/problems", response_model=list[ProblemRead])
def read_user_problems(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[ProblemRead]:
    return CRUDUser(session, api_user).read_user_problems(user_id)


@router.get("/{user_id}/datasets", response_model=list[DatasetRead])
def read_user_datasets(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[DatasetRead]:
    return CRUDUser(session, api_user).read_user_datasets(user_id)


@router.get("/{user_id}/issues", response_model=list[IssueRead])
def read_user_issues(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssueRead]:
    return CRUDUser(session, api_user).read_user_issues(user_id)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    *,
    user_id: int,
    user_update: UserUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserRead:
    return CRUDUser(session, api_user).update(user_id, user_update)


@router.delete("/{user_id}", response_model=UserRead)
def delete_user(
    *,
    user_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> UserRead:
    return CRUDUser(session, api_user).delete(user_id)
