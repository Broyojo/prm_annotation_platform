from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.annotation import AnnotationRead
from app.schemas.dataset import DatasetRead
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemRead
from app.schemas.user import UserCreate, UserRead, UserUpdate


class CRUDUser(CRUDBase):
    def create(self, user_create: UserCreate) -> UserRead:
        if self.api_user.permissions != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-admin user cannot add new users",
            )

        db_user = User(**user_create.model_dump(), creator_id=self.api_user.id)
        try:
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return UserRead.model_validate(db_user)
        except Exception as e:
            self.session.rollback()
            raise e

    def read_db_user(self, user_id: int) -> User:
        db_user = self.session.get(User, user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found",
            )
        return db_user

    def read(self, user_id: int) -> UserRead:
        db_user = self.read_db_user(user_id)
        return UserRead.model_validate(db_user)

    def read_all(self) -> list[UserRead]:
        db_users = self.session.exec(select(User)).all()
        return [UserRead.model_validate(user) for user in db_users]

    def read_user_users(self, user_id) -> list[UserRead]:
        db_user = self.read_db_user(user_id)
        return [UserRead.model_validate(user) for user in db_user.users]

    def read_user_datasets(self, user_id) -> list[DatasetRead]:
        db_user = self.read_db_user(user_id)
        return [DatasetRead.model_validate(dataset) for dataset in db_user.datasets]

    def read_user_problems(self, user_id) -> list[ProblemRead]:
        db_user = self.read_db_user(user_id)
        return [ProblemRead.model_validate(problem) for problem in db_user.problems]

    def read_user_annotations(self, user_id) -> list[AnnotationRead]:
        db_user = self.read_db_user(user_id)
        return [
            AnnotationRead.model_validate(annotation)
            for annotation in db_user.annotations
        ]

    def read_user_issues(self, user_id) -> list[IssueRead]:
        db_user = self.read_db_user(user_id)
        return [IssueRead.model_validate(issue) for issue in db_user.issues]

    def update(self, user_id: int, user_update: UserUpdate) -> UserRead:
        db_user = self.read_db_user(user_id)
        try:
            db_user = db_user.sqlmodel_update(
                user_update.model_dump(exclude_unset=True)
            )
            db_user.last_modified = datetime.now()
            self.session.add(db_user)
            self.session.commit()
            self.session.refresh(db_user)
            return UserRead.model_validate(db_user)
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, user_id) -> UserRead:
        if self.api_user.permissions != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Non-admin user cannot delete users",
            )

        db_user = self.read_db_user(user_id)
        try:
            self.session.delete(db_user)
            self.session.commit()
            return UserRead.model_validate(db_user)
        except Exception as e:
            self.session.rollback()
            raise e
