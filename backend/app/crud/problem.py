from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from app.crud.base import CRUDBase
from app.models.problem import Problem
from app.schemas.annotation import AnnotationRead
from app.schemas.issue import IssueRead
from app.schemas.problem import ProblemCreate, ProblemRead, ProblemUpdate


class CRUDProblem(CRUDBase):
    def create(self, problem_create: ProblemCreate) -> ProblemRead:
        db_problem = Problem(**problem_create.model_dump(), creator_id=self.api_user.id)
        try:
            self.session.add(db_problem)
            self.session.commit()
            self.session.refresh(db_problem)
            return ProblemRead.model_validate(db_problem)
        except Exception as e:
            self.session.rollback()
            raise e

    def read_db_problem(self, problem_id) -> Problem:
        db_problem = self.session.get(Problem, problem_id)
        if db_problem is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Problem with id {problem_id} not found",
            )
        return db_problem

    def read(self, problem_id: int) -> ProblemRead:
        db_problem = self.read_db_problem(problem_id)
        return ProblemRead.model_validate(db_problem)

    def read_all(self) -> list[ProblemRead]:
        db_problems = self.session.exec(select(Problem)).all()
        return [ProblemRead.model_validate(problem) for problem in db_problems]

    def read_problem_annotations(self, problem_id) -> list[AnnotationRead]:
        db_problem = self.read_db_problem(problem_id)
        return [
            AnnotationRead.model_validate(annotation)
            for annotation in db_problem.annotations
        ]

    def read_problem_issues(self, problem_id) -> list[IssueRead]:
        db_problem = self.read_db_problem(problem_id)
        return [IssueRead.model_validate(issue) for issue in db_problem.issues]

    def update(self, problem_id: int, problem_update: ProblemUpdate) -> ProblemRead:
        db_problem = self.read_db_problem(problem_id)
        try:
            db_problem = db_problem.sqlmodel_update(
                problem_update.model_dump(exclude_unset=True)
            )
            db_problem.last_modified = datetime.now()
            self.session.add(db_problem)
            self.session.commit()
            self.session.refresh(db_problem)
            return ProblemRead.model_validate(db_problem)
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, problem_id) -> ProblemRead:
        db_problem = self.read_db_problem(problem_id)
        try:
            self.session.delete(db_problem)
            self.session.commit()
            self.session.refresh(db_problem)
            return ProblemRead.model_validate(db_problem)
        except Exception as e:
            self.session.rollback()
            raise e
