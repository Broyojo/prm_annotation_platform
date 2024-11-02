from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.api.dependencies import get_api_user, get_session
from app.crud.dataset import CRUDDataset
from app.models.user import User
from app.schemas.annotation import AnnotationRead
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemRead

router = APIRouter()


@router.post("/", response_model=DatasetRead)
def create_dataset(
    *,
    dataset_create: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetRead:
    return CRUDDataset(session, api_user).create(dataset_create)


@router.get("/", response_model=list[DatasetRead])
def read_datasets(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[DatasetRead]:
    return CRUDDataset(session, api_user).read_all()


@router.get("/{dataset_id}", response_model=DatasetRead)
def read_dataset(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetRead:
    return CRUDDataset(session, api_user).read(dataset_id)


@router.get("/{dataset_id}/annotations", response_model=list[AnnotationRead])
def read_dataset_annotations(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationRead]:
    return CRUDDataset(session, api_user).read_dataset_annotations(dataset_id)


@router.get("/{dataset_id}/problems", response_model=list[ProblemRead])
def read_dataset_problems(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[ProblemRead]:
    return CRUDDataset(session, api_user).read_dataset_problems(dataset_id)


@router.get("/{dataset_id}/issues", response_model=list[DatasetRead])
def read_dataset_issues(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssueRead]:
    return CRUDDataset(session, api_user).read_dataset_issues(dataset_id)


@router.patch("/{dataset_id}", response_model=DatasetRead)
def update_dataset(
    *,
    dataset_id: int,
    dataset_update: DatasetUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetRead:
    return CRUDDataset(session, api_user).update(dataset_id, dataset_update)


@router.delete("/{dataset_id}", response_model=DatasetRead)
def delete_dataset(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetRead:
    return CRUDDataset(session, api_user).delete(dataset_id)
