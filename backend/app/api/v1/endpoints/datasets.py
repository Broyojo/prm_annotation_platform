from app.api.dependencies import get_api_user, get_session
from app.crud.dataset import CRUDDataset
from app.models.user import User
from app.schemas.annotation import AnnotationPublic
from app.schemas.dataset import DatasetCreate, DatasetPublic, DatasetUpdate
from app.schemas.issue import IssuePublic
from app.schemas.problem import ProblemPublic
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=DatasetPublic)
def create_dataset(
    *,
    dataset_create: DatasetCreate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetPublic:
    dataset = CRUDDataset(session).create(dataset_create)
    return dataset


@router.get("/", response_model=list[DatasetPublic])
def read_datasets(
    *, session: Session = Depends(get_session), api_user: User = Depends(get_api_user)
) -> list[DatasetPublic]:
    datasets = CRUDDataset(session).read_all()
    return datasets


@router.get("/{dataset_id}", response_model=DatasetPublic)
def read_dataset(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetPublic:
    dataset = CRUDDataset(session).read(dataset_id)
    return dataset


@router.patch("/{dataset_id}", response_model=DatasetPublic)
def update_dataset(
    *,
    dataset_id: int,
    dataset_update: DatasetUpdate,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> DatasetPublic:
    dataset = CRUDDataset(session).update(dataset_id, dataset_update)
    return dataset


@router.delete("/{dataset_id}")
def delete_dataset(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
):
    CRUDDataset(session).delete(dataset_id)


@router.get("/{dataset_id}/annotations", response_model=list[AnnotationPublic])
def read_dataset_annotations(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[AnnotationPublic]:
    pass


@router.get("/{dataset_id}/problems", response_model=list[ProblemPublic])
def read_dataset_problems(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[ProblemPublic]:
    pass


@router.get("/{dataset_id}/issues", response_model=list[IssuePublic])
def read_dataset_issues(
    *,
    dataset_id: int,
    session: Session = Depends(get_session),
    api_user: User = Depends(get_api_user)
) -> list[IssuePublic]:
    pass
