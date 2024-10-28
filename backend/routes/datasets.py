from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/datasets", tags=["Datasets"])
from models import Dataset, DatasetPublic, Problem, ProblemPublic


@router.get("/", response_model=list[DatasetPublic])
async def read_datasets(session: Session = Depends(get_session)):
    return session.exec(select(Dataset)).all()


@router.get("/{dataset_id}", response_model=DatasetPublic)
async def read_dataset(dataset_id: int, session: Session = Depends(get_session)):
    dataset = session.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/problems", response_model=list[ProblemPublic])
async def read_dataset_problems(
    dataset_id: int, session: Session = Depends(get_session)
):
    if not session.get(Dataset, dataset_id):
        raise HTTPException(status_code=404, detail="Dataset not found")
    query = select(Problem).where(Problem.dataset_id == dataset_id)
    problems = session.exec(query).all()
    return problems
