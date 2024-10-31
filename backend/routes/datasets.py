from datetime import datetime

from database import get_session
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

router = APIRouter(prefix="/datasets", tags=["Datasets"])
from models import Dataset, DatasetCreate, DatasetPublic, Problem, ProblemPublic


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
    if session.get(Dataset, dataset_id) is None:
        raise HTTPException(status_code=404, detail="Dataset not found")
    query = select(Problem).where(Problem.dataset_id == dataset_id)
    problems = session.exec(query).all()
    return problems


@router.post("/{dataset_id}", response_model=DatasetPublic)
async def create_dataset(
    dataset: DatasetCreate, session: Session = Depends(get_session)
):
    db_dataset = Dataset(
        **dataset.model_dump(exclude={"problems"}),
        created_at=datetime.now(),
        last_modified=datetime.now()
    )
    session.add(db_dataset)

    if dataset.problems:
        for problem_data in dataset.problems:
            db_problem = Problem(
                **problem_data.model_dump(),
                dataset_id=db_dataset.id,
                created_at=datetime.now(),
                last_modified=datetime.now()
            )
            session.add(db_problem)

    session.commit()
    session.refresh(db_dataset)
    return db_dataset
