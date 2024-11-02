from datetime import datetime

from fastapi import HTTPException, status
from sqlmodel import select

from app.crud.base import CRUDBase
from app.crud.problem import CRUDProblem
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueRead, IssueUpdate


class CRUDIssue(CRUDBase):
    def create(self, issue_create: IssueCreate) -> IssueRead:
        db_issue = Issue(**issue_create.model_dump(), creator_id=self.api_user.id)
        CRUDProblem(self.session, self.api_user).read(issue_create.problem_id)
        try:
            self.session.add(db_issue)
            self.session.commit()
            self.session.refresh(db_issue)
            return IssueRead.model_validate(db_issue)
        except Exception as e:
            self.session.rollback()
            raise e

    def read_db_issue(self, issue_id) -> Issue:
        db_issue = self.session.get(Issue, issue_id)
        if db_issue is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Issue with id {issue_id} not found",
            )
        return db_issue

    def read(self, issue_id: int) -> IssueRead:
        db_issue = self.read_db_issue(issue_id)
        return IssueRead.model_validate(db_issue)

    def read_all(self) -> list[IssueRead]:
        db_issues = self.session.exec(select(Issue)).all()
        return [IssueRead.model_validate(issue) for issue in db_issues]

    def update(self, issue_id: int, issue_update: IssueUpdate) -> IssueRead:
        db_issue = self.read_db_issue(issue_id)
        try:
            db_issue = db_issue.sqlmodel_update(
                issue_update.model_dump(exclude_unset=True)
            )
            db_issue.last_modified = datetime.now()
            self.session.add(db_issue)
            self.session.commit()
            self.session.refresh(db_issue)
            return IssueRead.model_validate(db_issue)
        except Exception as e:
            self.session.rollback()
            raise e

    def delete(self, issue_id) -> IssueRead:
        db_issue = self.read_db_issue(issue_id)
        try:
            self.session.delete(db_issue)
            self.session.commit()
            return IssueRead.model_validate(db_issue)
        except Exception as e:
            self.session.rollback()
            raise e
