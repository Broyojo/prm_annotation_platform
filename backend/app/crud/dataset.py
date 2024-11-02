from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from app.crud.base import CRUDBase
from app.models.dataset import Dataset
from app.models.problem import Problem
from app.schemas.annotation import AnnotationRead
from app.schemas.dataset import DatasetCreate, DatasetRead, DatasetUpdate
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemRead


class CRUDDataset(CRUDBase):
    def create(self, dataset_create: DatasetCreate) -> DatasetRead:
        problems = [
            Problem(**problem.model_dump(), creator_id=self.api_user.id)
            for problem in dataset_create.problems
        ]
        db_dataset = Dataset(
            **dataset_create.model_dump(exclude={"problems": True}),
            problems=problems,
            creator_id=self.api_user.id,
        )
        try:
            self.session.add(db_dataset)
            self.session.commit()
            self.session.refresh(db_dataset)
            return DatasetRead.model_validate(db_dataset)
        except Exception as e:
            self.session.rollback()
            raise e

    def read_db_dataset(self, dataset_id) -> Dataset:
        db_dataset = self.session.get(Dataset, dataset_id)
        if db_dataset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Problem with id {dataset_id} not found",
            )
        return db_dataset

    def read(self, dataset_id: int) -> DatasetRead:
        db_dataset = self.read_db_dataset(dataset_id)
        return DatasetRead.model_validate(db_dataset)

    def read_all(self) -> list[DatasetRead]:
        db_datasets = self.session.exec(select(Dataset)).all()
        return [DatasetRead.model_validate(dataset) for dataset in db_datasets]

    def read_dataset_problems(self, dataset_id) -> list[ProblemRead]:
        db_dataset = self.read_db_dataset(dataset_id)
        return [ProblemRead.model_validate(problem) for problem in db_dataset.problems]

    def read_dataset_annotations(self, dataset_id) -> list[AnnotationRead]:
        db_dataset = self.read_db_dataset(dataset_id)
        annotations = []
        for problem in db_dataset.problems:
            annotations.extend(
                [
                    AnnotationRead.model_validate(annotation)
                    for annotation in problem.annotations
                ]
            )
        return annotations

    def read_dataset_issues(self, dataset_id) -> list[IssueRead]:
        db_dataset = self.read_db_dataset(dataset_id)
        issues = []
        for problem in db_dataset.problems:
            issues.extend([IssueRead.model_validate(issue) for issue in problem.issues])
        return issues

    def update(self, dataset_id: int, dataset_update: DatasetUpdate) -> DatasetRead:
        db_dataset = self.read_db_dataset(dataset_id)
        try:
            db_dataset = db_dataset.sqlmodel_update(
                dataset_update.model_dump(exclude_unset=True)
            )
            db_dataset.last_modified = datetime.now()
            self.session.add(db_dataset)
            self.session.commit()
            self.session.refresh(db_dataset)
            return DatasetRead.model_validate(db_dataset)
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, dataset_id) -> DatasetRead:
        if self.api_user.permissions != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-admin user cannot delete datasets",
            )

        db_dataset = self.read_db_dataset(dataset_id)
        try:
            self.session.delete(db_dataset)
            self.session.commit()
            return DatasetRead.model_validate(db_dataset)
        except Exception as e:
            self.session.rollback()
            raise e
