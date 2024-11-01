from app.api.dependencies import get_session
from app.crud.issue import CRUDIssue
from app.schemas.issue import IssueCreate, IssuePublic, IssueUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

router = APIRouter()


@router.post("/", response_model=IssuePublic)
def create_issue(
    *, issue_create: IssueCreate, session: Session = Depends(get_session)
) -> IssuePublic:
    issue = CRUDIssue(session).create(issue_create)
    return issue


@router.get("/", response_model=list[IssuePublic])
def read_issues(*, session: Session = Depends(get_session)) -> list[IssuePublic]:
    issues = CRUDIssue(session).read_all()
    return issues


@router.get("/{issue_id}", response_model=IssuePublic)
def read_issue(
    *, issue_id: int, session: Session = Depends(get_session)
) -> IssuePublic:
    issue = CRUDIssue(session).read(issue_id)
    return issue


@router.patch("/{issue_id}", response_model=IssuePublic)
def update_issue(
    *, issue_id: int, issue_update: IssueUpdate, session: Session = Depends(get_session)
) -> IssuePublic:
    issue = CRUDIssue(session).update(issue_id, issue_update)
    return issue


@router.delete("/{issue_id}")
def delete_issue(*, issue_id: int, session: Session = Depends(get_session)):
    CRUDIssue(session).delete(issue_id)
