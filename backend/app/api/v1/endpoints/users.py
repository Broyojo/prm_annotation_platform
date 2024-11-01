from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from ....api.dependencies import get_session
from ....models.user import User
from ....schemas.annotation import AnnotationPublic
from ....schemas.dataset import DatasetPublic
from ....schemas.issue import IssuePublic
from ....schemas.problem import ProblemPublic
from ....schemas.user import UserPublic, UserUpdate

router = APIRouter()


@router.post("/", response_model=UserPublic)
def create_user(*, session: Session = get_session()) -> UserPublic:
    pass


@router.get("/", response_model=list[UserPublic])
def read_users(*, session: Session = get_session()) -> list[UserPublic]:
    pass


@router.get("/{user_id}", response_model=UserPublic)
def read_user(*, user_id: int, session: Session = get_session()) -> UserPublic:
    pass


@router.get("/{user_id}", response_model=list[UserPublic])
def read_user_users(
    *, user_id: int, session: Session = get_session()
) -> list[UserPublic]:
    pass


@router.get("/{user_id}", response_model=list[AnnotationPublic])
def read_user_annotations(
    *, user_id: int, session: Session = get_session()
) -> list[AnnotationPublic]:
    pass


@router.get("/{user_id}", response_model=list[ProblemPublic])
def read_user_problems(
    *, user_id: int, session: Session = get_session()
) -> list[ProblemPublic]:
    pass


@router.get("/{user_id}", response_model=list[DatasetPublic])
def read_user_datasets(
    *, user_id: int, session: Session = get_session()
) -> list[DatasetPublic]:
    pass


@router.get("/{user_id}", response_model=list[IssuePublic])
def read_user_issues(
    *, user_id: int, session: Session = get_session()
) -> list[IssuePublic]:
    pass


@router.patch("/{user_id}", response_model=UserPublic)
def update_user(
    *, user_id: int, user_update: UserUpdate, session: Session = get_session()
) -> UserPublic:
    pass


@router.delete("/{user_id}")
def delete_user(*, user_id: int, session: Session = get_session()):
    pass
